# app_kernel.py
import asyncio
import logging
import uuid
from typing import Dict, List, Optional

# FastAPI imports
from fastapi import FastAPI, HTTPException, Query, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Initialize the FastAPI app first with basic health endpoint
app = FastAPI(
    title="Darbot Agent Engine API",
    description="""
    ## Multi-Agent Custom Automation Engine
    
    This API provides endpoints for managing AI agents, tasks, and multi-agent workflows.
    
    ### Key Features:
    - **Agent Management**: Create and manage different types of AI agents
    - **Task Processing**: Submit tasks for AI agent processing  
    - **Multi-Agent Workflows**: Coordinate multiple agents for complex tasks
    - **Health Monitoring**: Monitor service and dependency health
    
    ### Authentication:
    Most endpoints require authentication via Azure AD tokens.
    
    ### Rate Limits:
    API calls are subject to rate limiting based on Azure service quotas.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Darbot Agent Engine Support",
        "url": "https://github.com/darbotlabs/Darbot-Agent-Engine",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    tags_metadata=[
        {
            "name": "health",
            "description": "Health check and monitoring endpoints",
        },
        {
            "name": "agents", 
            "description": "Agent management and interaction endpoints",
        },
        {
            "name": "tasks",
            "description": "Task submission and processing endpoints", 
        },
        {
            "name": "info",
            "description": "Server information and configuration endpoints",
        },
    ]
)

# CRITICAL: Add the primary health endpoint first, before any complex imports
# This ensures the launcher health check always works, even if dependencies fail
@app.get("/health", tags=["health"])
async def get_basic_health():
    """
    Basic health check endpoint for simple monitoring and launcher scripts.
    
    Returns 200 if the service is running. This is the primary health endpoint
    used by the Launcher.ps1 script and other monitoring tools.
    
    This endpoint is designed to be fast and dependency-free to ensure
    it always responds even if other parts of the system have issues.
    """
    return {"status": "ok", "service": "Darbot Agent Engine"}

# Now import optional dependencies with error handling
try:
    from .app_config import config  # Thought into existence by Darbot
except (ImportError, ValueError) as e:
    logging.warning(f"Failed to import app_config: {e}")
    config = None

try:
    from .auth.auth_utils import get_authenticated_user_details, user_has_role  # Thought into existence by Darbot
except ImportError as e:
    logging.warning(f"Failed to import auth utils: {e}")
    def get_authenticated_user_details(*args, **kwargs):
        return {"user_principal_id": "test-user"}
    def user_has_role(*args, **kwargs):
        return True

# Azure monitoring
try:
    from .config_kernel import Config  # Thought into existence by Darbot
except (ImportError, ValueError) as e:
    logging.warning(f"Failed to import config_kernel: {e}")
    class Config:
        FRONTEND_SITE_NAME = "http://localhost:3000"

try:
    from .event_utils import track_event_if_configured  # Thought into existence by Darbot
except ImportError as e:
    logging.warning(f"Failed to import event_utils: {e}")
    def track_event_if_configured(*args, **kwargs):
        pass

# Local imports with error handling
try:
    from .kernel_agents.agent_factory import AgentFactory  # Thought into existence by Darbot
except ImportError as e:
    logging.warning(f"Failed to import AgentFactory: {e}")
    class AgentFactory:
        @staticmethod
        async def create_all_agents(*args, **kwargs):
            return {}
        @staticmethod
        async def create_agent(*args, **kwargs):
            return None
        @staticmethod
        def clear_cache():
            pass

try:
    from .middleware.health_check import HealthCheckMiddleware
except ImportError as e:
    logging.warning(f"Failed to import HealthCheckMiddleware: {e}")
    HealthCheckMiddleware = None

try:
    from .models.custom_exceptions import DarbotEngineException
except ImportError as e:
    logging.warning(f"Failed to import DarbotEngineException: {e}")
    class DarbotEngineException(Exception):
        def __init__(self, detail, status_code=500, error_code="DARBOT_ERROR", extra_data=None):
            self.detail = detail
            self.status_code = status_code
            self.error_code = error_code
            self.extra_data = extra_data or {}

try:
    from .models.messages_kernel import (
        AgentMessage,
        AgentType,
        HumanClarification,
        HumanFeedback,
        InputTask,
        PlanWithSteps,
        Step,
    )
except ImportError as e:
    logging.warning(f"Failed to import message models: {e}")
    # Create mock Pydantic classes for FastAPI compatibility
    from pydantic import BaseModel
    from typing import List, Optional
    
    class AgentMessage(BaseModel):
        id: Optional[str] = None
        content: Optional[str] = None
        
    class AgentType:
        GROUP_CHAT_MANAGER = "group_chat_manager"
        HUMAN = "human"
        value = "mock_agent"
        
    class HumanClarification(BaseModel):
        session_id: Optional[str] = None
        plan_id: Optional[str] = None
        human_clarification: Optional[str] = None
        step_id: Optional[str] = None
        
    class HumanFeedback(BaseModel):
        session_id: Optional[str] = None
        step_id: Optional[str] = None
        plan_id: Optional[str] = None
        approved: Optional[bool] = None
        human_feedback: Optional[str] = None
        updated_action: Optional[str] = None
        
    class InputTask(BaseModel):
        session_id: Optional[str] = None
        description: Optional[str] = None
        
    class PlanWithSteps(BaseModel):
        id: Optional[str] = None
        session_id: Optional[str] = None
        steps: Optional[List] = []
        
        def update_step_counts(self):
            pass
            
    class Step(BaseModel):
        id: Optional[str] = None
        plan_id: Optional[str] = None
        action: Optional[str] = None

# Updated import for KernelArguments
try:
    from .utils_kernel import initialize_runtime_and_context, rai_success
except ImportError as e:
    logging.warning(f"Failed to import utils_kernel: {e}")
    async def initialize_runtime_and_context(*args, **kwargs):
        return None, None
    async def rai_success(*args, **kwargs):
        return True

# # Check if the Application Insights Instrumentation Key is set in the environment variables
# connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
# if connection_string:
#     # Configure Application Insights if the Instrumentation Key is found
#     configure_azure_monitor(connection_string=connection_string)
#     logging.info(
#         "Application Insights configured with the provided Instrumentation Key"
#     )
# else:
#     # Log a warning if the Instrumentation Key is not found
#     logging.warning(
#         "No Application Insights Instrumentation Key found. Skipping configuration"
#     )

# Configure logging before any other operations
try:
    from .utils.logging_config import configure_for_environment, get_logger
    configure_for_environment()
    logger = get_logger(__name__)
except ImportError as e:
    logging.warning(f"Failed to import logging config: {e}")
    logger = logging.getLogger(__name__)

# Suppress INFO logs from 'azure.core.pipeline.policies.http_logging_policy'
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
    logging.WARNING
)
logging.getLogger("azure.identity.aio._internal").setLevel(logging.WARNING)

# # Suppress info logs from OpenTelemetry exporter
logging.getLogger("azure.monitor.opentelemetry.exporter.export._base").setLevel(
    logging.WARNING
)

# Add a /healthz endpoint for compatibility with all launchers and scripts
health_router = APIRouter()

@health_router.get("/healthz", tags=["health"])
async def healthz_endpoint():
    """
    Healthz endpoint for middleware compatibility.
    Returns 200 if the service is running.
    """
    return {"status": "ok", "service": "Darbot Agent Engine"}

app.include_router(health_router)

# Global exception handlers for enhanced error responses
@app.exception_handler(DarbotEngineException)
async def darbot_exception_handler(request: Request, exc: DarbotEngineException):
    """Handle custom Darbot exceptions with structured error responses"""
    logging.error(f"DarbotEngineException: {exc.detail}", extra={
        "error_code": exc.error_code,
        "status_code": exc.status_code,
        "extra_data": exc.extra_data,
        "path": request.url.path
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.detail,
                "details": exc.extra_data,
                "path": request.url.path,
                "timestamp": str(asyncio.get_event_loop().time())
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors with detailed field information"""
    logging.warning(f"Validation error: {exc.errors()}", extra={
        "path": request.url.path,
        "errors": exc.errors()
    })
    
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {
                    "validation_errors": exc.errors()
                },
                "path": request.url.path,
                "timestamp": str(asyncio.get_event_loop().time())
            }
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with consistent error format"""
    logging.warning(f"HTTP exception: {exc.detail}", extra={
        "status_code": exc.status_code,
        "path": request.url.path
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "details": {},
                "path": request.url.path,
                "timestamp": str(asyncio.get_event_loop().time())
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions with generic error response"""
    logging.exception("Unexpected error occurred", extra={
        "path": request.url.path,
        "exception_type": type(exc).__name__
    })
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": {
                    "exception_type": type(exc).__name__
                },
                "path": request.url.path,
                "timestamp": str(asyncio.get_event_loop().time())
            }
        }
    )

# Thought into existence by Darbot - Add server info endpoint
@app.get("/api/server-info", tags=["info"])
async def get_server_info():
    """Get server configuration information."""
    return {
        "service": "Darbot Agent Engine",
        "version": "1.0.0",
        "backend_host": config.BACKEND_HOST,
        "backend_port": config.BACKEND_PORT,
        "frontend_url": config.FRONTEND_SITE_NAME,
        "status": "running"
    }

# Enhanced health check endpoint
@app.get("/api/health", tags=["health"])
async def get_health_detailed():
    """
    Get detailed health status including dependency checks.
    
    Returns comprehensive health information about the service and its dependencies
    including CosmosDB, Azure OpenAI, and other critical services.
    """
    try:
        from .middleware.dependency_health_checks import create_health_checks
        
        health_checks = await create_health_checks(config)
        results = {}
        overall_status = True
        
        # Run all health checks
        for name, check_func in health_checks.items():
            try:
                result = await check_func()
                results[name] = {
                    "status": "healthy" if result.status else "unhealthy",
                    "message": result.message
                }
                overall_status = overall_status and result.status
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "message": f"Health check failed: {str(e)}"
                }
                overall_status = False
        
        response = {
            "overall_status": "healthy" if overall_status else "unhealthy",
            "service": "Darbot Agent Engine",
            "version": "1.0.0",
            "checks": results,
            "timestamp": str(asyncio.get_event_loop().time())
        }
        
        return response
        
    except Exception as e:
        logging.exception("Error in detailed health check")
        return {
            "overall_status": "error",
            "service": "Darbot Agent Engine", 
            "version": "1.0.0",
            "error": f"Health check system error: {str(e)}",
            "timestamp": str(asyncio.get_event_loop().time())
        }

@app.get("/api/health/ready", tags=["health"])
async def get_readiness():
    """
    Readiness probe endpoint for container orchestration.
    
    Returns 200 if the service is ready to accept traffic.
    """
    try:
        # Basic readiness check - verify critical configuration
        if not config.AZURE_AI_SUBSCRIPTION_ID:
            raise HTTPException(status_code=503, detail="Azure AI subscription not configured")
        
        if not config.AZURE_OPENAI_ENDPOINT:
            raise HTTPException(status_code=503, detail="Azure OpenAI endpoint not configured")
        
        return {"status": "ready", "service": "Darbot Agent Engine"}
        
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("Error in readiness check")
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")

@app.get("/api/health/live", tags=["health"])
async def get_liveness():
    """
    Liveness probe endpoint for container orchestration.
    
    Returns 200 if the service is alive and responding.
    """
    return {"status": "alive", "service": "Darbot Agent Engine"}

# Remove duplicate health endpoint - the primary one is defined at the top

frontend_url = Config.FRONTEND_SITE_NAME

# Add this near the top of your app.py, after initializing the app
app.add_middleware(
    CORSMiddleware,
    # Allow all origins during development (more permissive for testing)
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure health check with enhanced dependency checks
try:
    from .middleware.dependency_health_checks import create_health_checks
except ImportError as e:
    logging.warning(f"Failed to import dependency health checks: {e}")
    async def create_health_checks(config):
        return {}

# Create health checks asynchronously when needed
async def setup_health_checks():
    """Set up enhanced health checks for dependencies"""
    try:
        health_checks = await create_health_checks(config)
        return health_checks
    except Exception as e:
        logging.error(f"Failed to create health checks: {e}")
        return {}

# Configure health check middleware with enhanced checks
if HealthCheckMiddleware:
    try:
        # For now, use a simple synchronous approach
        # The health checks will be created when the middleware is called
        app.add_middleware(HealthCheckMiddleware, password="", checks={})
        logging.info("Added health check middleware with enhanced dependency checks")
    except Exception as e:
        logging.error(f"Failed to add health check middleware: {e}")
else:
    logging.info("HealthCheckMiddleware not available, skipping middleware setup")


@app.post("/api/input_task")
async def input_task_endpoint(input_task: InputTask, request: Request):
    """
    Receive the initial input task from the user.
    """
    # Fix 1: Properly await the async rai_success function
    if not await rai_success(input_task.description):
        print("RAI failed")

        track_event_if_configured(
            "RAI failed",
            {
                "status": "Plan not created",
                "description": input_task.description,
                "session_id": input_task.session_id,
            },
        )

        return {
            "status": "Plan not created",
        }
    authenticated_user = get_authenticated_user_details(request_headers=request.headers)
    user_id = authenticated_user["user_principal_id"]

    if not user_id:
        track_event_if_configured(
            "UserIdNotFound", {"status_code": 400, "detail": "no user"}
        )
        raise HTTPException(status_code=400, detail="no user")

    # Generate session ID if not provided
    if not input_task.session_id:
        input_task.session_id = str(uuid.uuid4())

    try:
        # Create all agents instead of just the planner agent
        # This ensures other agents are created first and the planner has access to them
        kernel, memory_store = await initialize_runtime_and_context(
            input_task.session_id, user_id
        )
        client = None
        try:
            client = config.get_ai_project_client()
        except Exception as client_exc:
            logging.error(f"Error creating AIProjectClient: {client_exc}")

        agents = await AgentFactory.create_all_agents(
            session_id=input_task.session_id,
            user_id=user_id,
            memory_store=memory_store,
            client=client,
        )

        group_chat_manager = agents[AgentType.GROUP_CHAT_MANAGER.value]

        # Convert input task to JSON for the kernel function, add user_id here

        # Use the planner to handle the task
        result = await group_chat_manager.handle_input_task(input_task)

        print(f"Result: {result}")
        # Get plan from memory store
        plan = await memory_store.get_plan_by_session(input_task.session_id)

        if not plan:  # If the plan is not found, raise an error
            track_event_if_configured(
                "PlanNotFound",
                {
                    "status": "Plan not found",
                    "session_id": input_task.session_id,
                    "description": input_task.description,
                },
            )
            raise HTTPException(status_code=404, detail="Plan not found")
        # Log custom event for successful input task processing
        track_event_if_configured(
            "InputTaskProcessed",
            {
                "status": f"Plan created with ID: {plan.id}",
                "session_id": input_task.session_id,
                "plan_id": plan.id,
                "description": input_task.description,
            },
        )
        if client:
            try:
                client.close()
            except Exception as e:
                logging.error(f"Error sending to AIProjectClient: {e}")
        return {
            "status": f"Plan created with ID: {plan.id}",
            "session_id": input_task.session_id,
            "plan_id": plan.id,
            "description": input_task.description,
        }

    except Exception as e:
        logging.exception(f"Error handling input task: {e}")
        track_event_if_configured(
            "InputTaskError",
            {
                "session_id": input_task.session_id,
                "description": input_task.description,
                "error": str(e),
            },
        )
        raise HTTPException(status_code=400, detail="Error creating plan")


@app.post("/api/human_feedback")
async def human_feedback_endpoint(human_feedback: HumanFeedback, request: Request):
    """
    Receive human feedback on a step.

    ---
    tags:
      - Feedback
    parameters:
      - name: user_principal_id
        in: header
        type: string
        required: true
        description: User ID extracted from the authentication header
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            step_id:
              type: string
              description: The ID of the step to provide feedback for
            plan_id:
              type: string
              description: The plan ID
            session_id:
              type: string
              description: The session ID
            approved:
              type: boolean
              description: Whether the step is approved
            human_feedback:
              type: string
              description: Optional feedback details
            updated_action:
              type: string
              description: Optional updated action
            user_id:
              type: string
              description: The user ID providing the feedback
    responses:
      200:
        description: Feedback received successfully
        schema:
          type: object
          properties:
            status:
              type: string
            session_id:
              type: string
            step_id:
              type: string
      400:
        description: Missing or invalid user information
    """
    authenticated_user = get_authenticated_user_details(request_headers=request.headers)
    user_id = authenticated_user["user_principal_id"]
    if not user_id:
        track_event_if_configured(
            "UserIdNotFound", {"status_code": 400, "detail": "no user"}
        )
        raise HTTPException(status_code=400, detail="no user")

    kernel, memory_store = await initialize_runtime_and_context(
        human_feedback.session_id, user_id
    )

    client = None
    try:
        client = config.get_ai_project_client()
    except Exception as client_exc:
        logging.error(f"Error creating AIProjectClient: {client_exc}")

    human_agent = await AgentFactory.create_agent(
        agent_type=AgentType.HUMAN,
        session_id=human_feedback.session_id,
        user_id=user_id,
        memory_store=memory_store,
        client=client,
    )

    if human_agent is None:
        track_event_if_configured(
            "AgentNotFound",
            {
                "status": "Agent not found",
                "session_id": human_feedback.session_id,
                "step_id": human_feedback.step_id,
            },
        )
        raise HTTPException(status_code=404, detail="Agent not found")

    # Use the human agent to handle the feedback
    await human_agent.handle_human_feedback(human_feedback=human_feedback)

    track_event_if_configured(
        "Completed Feedback received",
        {
            "status": "Feedback received",
            "session_id": human_feedback.session_id,
            "step_id": human_feedback.step_id,
        },
    )
    if client:
        try:
            client.close()
        except Exception as e:
            logging.error(f"Error sending to AIProjectClient: {e}")
    return {
        "status": "Feedback received",
        "session_id": human_feedback.session_id,
        "step_id": human_feedback.step_id,
    }


@app.post("/api/human_clarification_on_plan")
async def human_clarification_endpoint(
    human_clarification: HumanClarification, request: Request
):
    """
    Receive human clarification on a plan.

    ---
    tags:
      - Clarification
    parameters:
      - name: user_principal_id
        in: header
        type: string
        required: true
        description: User ID extracted from the authentication header
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            plan_id:
              type: string
              description: The plan ID requiring clarification
            session_id:
              type: string
              description: The session ID
            human_clarification:
              type: string
              description: Clarification details provided by the user
            user_id:
              type: string
              description: The user ID providing the clarification
    responses:
      200:
        description: Clarification received successfully
        schema:
          type: object
          properties:
            status:
              type: string
            session_id:
              type: string
      400:
        description: Missing or invalid user information
    """
    authenticated_user = get_authenticated_user_details(request_headers=request.headers)
    user_id = authenticated_user["user_principal_id"]
    if not user_id:
        track_event_if_configured(
            "UserIdNotFound", {"status_code": 400, "detail": "no user"}
        )
        raise HTTPException(status_code=400, detail="no user")

    kernel, memory_store = await initialize_runtime_and_context(
        human_clarification.session_id, user_id
    )
    client = None
    try:
        client = config.get_ai_project_client()
    except Exception as client_exc:
        logging.error(f"Error creating AIProjectClient: {client_exc}")

    human_agent = await AgentFactory.create_agent(
        agent_type=AgentType.HUMAN,
        session_id=human_clarification.session_id,
        user_id=user_id,
        memory_store=memory_store,
        client=client,
    )

    if human_agent is None:
        track_event_if_configured(
            "AgentNotFound",
            {
                "status": "Agent not found",
                "session_id": human_clarification.session_id,
                "step_id": human_clarification.step_id,
            },
        )
        raise HTTPException(status_code=404, detail="Agent not found")

    # Use the human agent to handle the feedback
    await human_agent.handle_human_clarification(
        human_clarification=human_clarification
    )

    track_event_if_configured(
        "Completed Human clarification on the plan",
        {
            "status": "Clarification received",
            "session_id": human_clarification.session_id,
        },
    )
    if client:
        try:
            client.close()
        except Exception as e:
            logging.error(f"Error sending to AIProjectClient: {e}")
    return {
        "status": "Clarification received",
        "session_id": human_clarification.session_id,
    }


@app.post("/api/approve_step_or_steps")
async def approve_step_endpoint(
    human_feedback: HumanFeedback, request: Request
) -> Dict[str, str]:
    """
    Approve a step or multiple steps in a plan.

    ---
    tags:
      - Approval
    parameters:
      - name: user_principal_id
        in: header
        type: string
        required: true
        description: User ID extracted from the authentication header
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            step_id:
              type: string
              description: Optional step ID to approve
            plan_id:
              type: string
              description: The plan ID
            session_id:
              type: string
              description: The session ID
            approved:
              type: boolean
              description: Whether the step(s) are approved
            human_feedback:
              type: string
              description: Optional feedback details
            updated_action:
              type: string
              description: Optional updated action
            user_id:
              type: string
              description: The user ID providing the approval
    responses:
      200:
        description: Approval status returned
        schema:
          type: object
          properties:
            status:
              type: string
      400:
        description: Missing or invalid user information
    """
    authenticated_user = get_authenticated_user_details(request_headers=request.headers)
    user_id = authenticated_user["user_principal_id"]
    if not user_id:
        track_event_if_configured(
            "UserIdNotFound", {"status_code": 400, "detail": "no user"}
        )
        raise HTTPException(status_code=400, detail="no user")

    # Get the agents for this session
    kernel, memory_store = await initialize_runtime_and_context(
        human_feedback.session_id, user_id
    )
    client = None
    try:
        client = config.get_ai_project_client()
    except Exception as client_exc:
        logging.error(f"Error creating AIProjectClient: {client_exc}")
    agents = await AgentFactory.create_all_agents(
        session_id=human_feedback.session_id,
        user_id=user_id,
        memory_store=memory_store,
        client=client,
    )

    # Send the approval to the group chat manager
    group_chat_manager = agents[AgentType.GROUP_CHAT_MANAGER.value]

    await group_chat_manager.handle_human_feedback(human_feedback)

    if client:
        try:
            client.close()
        except Exception as e:
            logging.error(f"Error sending to AIProjectClient: {e}")
    # Return a status message
    if human_feedback.step_id:
        track_event_if_configured(
            "Completed Human clarification with step_id",
            {
                "status": f"Step {human_feedback.step_id} - Approval:{human_feedback.approved}."
            },
        )

        return {
            "status": f"Step {human_feedback.step_id} - Approval:{human_feedback.approved}."
        }
    else:
        track_event_if_configured(
            "Completed Human clarification without step_id",
            {"status": "All steps approved"},
        )

        return {"status": "All steps approved"}


@app.get("/api/plans", response_model=List[PlanWithSteps])
async def get_plans(
    request: Request, session_id: Optional[str] = Query(None)
) -> List[PlanWithSteps]:
    """
    Retrieve plans for the current user.

    ---
    tags:
      - Plans
    parameters:
      - name: session_id
        in: query
        type: string
        required: false
        description: Optional session ID to retrieve plans for a specific session
    responses:
      200:
        description: List of plans with steps for the user
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: string
                description: Unique ID of the plan
              session_id:
                type: string
                description: Session ID associated with the plan
              initial_goal:
                type: string
                description: The initial goal derived from the user's input
              overall_status:
                type: string
                description: Status of the plan (e.g., in_progress, completed)
              steps:
                type: array
                items:
                  type: object
                  properties:
                    id:
                      type: string
                      description: Unique ID of the step
                    plan_id:
                      type: string
                      description: ID of the plan the step belongs to
                    action:
                      type: string
                      description: The action to be performed
                    agent:
                      type: string
                      description: The agent responsible for the step
                    status:
                      type: string
                      description: Status of the step (e.g., planned, approved, completed)
      400:
        description: Missing or invalid user information
      404:
        description: Plan not found
    """
    authenticated_user = get_authenticated_user_details(request_headers=request.headers)
    user_id = authenticated_user["user_principal_id"]
    if not user_id:
        track_event_if_configured(
            "UserIdNotFound", {"status_code": 400, "detail": "no user"}
        )
        raise HTTPException(status_code=400, detail="no user")

    # Initialize memory context
    kernel, memory_store = await initialize_runtime_and_context(
        session_id or "", user_id
    )

    if session_id:
        plan = await memory_store.get_plan_by_session(session_id=session_id)
        if not plan:
            track_event_if_configured(
                "GetPlanBySessionNotFound",
                {"status_code": 400, "detail": "Plan not found"},
            )
            raise HTTPException(status_code=404, detail="Plan not found")

        # Use get_steps_by_plan to match the original implementation
        steps = await memory_store.get_steps_by_plan(plan_id=plan.id)
        plan_with_steps = PlanWithSteps(**plan.model_dump(), steps=steps)
        plan_with_steps.update_step_counts()
        return [plan_with_steps]

    all_plans = await memory_store.get_all_plans()
    # Fetch steps for all plans concurrently
    steps_for_all_plans = await asyncio.gather(
        *[memory_store.get_steps_by_plan(plan_id=plan.id) for plan in all_plans]
    )
    # Create list of PlanWithSteps and update step counts
    list_of_plans_with_steps = []
    for plan, steps in zip(all_plans, steps_for_all_plans):
        plan_with_steps = PlanWithSteps(**plan.model_dump(), steps=steps)
        plan_with_steps.update_step_counts()
        list_of_plans_with_steps.append(plan_with_steps)

    return list_of_plans_with_steps


@app.get("/api/steps/{plan_id}", response_model=List[Step])
async def get_steps_by_plan(plan_id: str, request: Request) -> List[Step]:
    """
    Retrieve steps for a specific plan.

    ---
    tags:
      - Steps
    parameters:
      - name: plan_id
        in: path
        type: string
        required: true
        description: The ID of the plan to retrieve steps for
    responses:
      200:
        description: List of steps associated with the specified plan
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: string
                description: Unique ID of the step
              plan_id:
                type: string
                description: ID of the plan the step belongs to
              action:
                type: string
                description: The action to be performed
              agent:
                type: string
                description: The agent responsible for the step
              status:
                type: string
                description: Status of the step (e.g., planned, approved, completed)
              agent_reply:
                type: string
                description: Optional response from the agent after execution
              human_feedback:
                type: string
                description: Optional feedback provided by a human
              updated_action:
                type: string
                description: Optional modified action based on feedback
       400:
        description: Missing or invalid user information
      404:
        description: Plan or steps not found
    """
    authenticated_user = get_authenticated_user_details(request_headers=request.headers)
    user_id = authenticated_user["user_principal_id"]
    if not user_id:
        track_event_if_configured(
            "UserIdNotFound", {"status_code": 400, "detail": "no user"}
        )
        raise HTTPException(status_code=400, detail="no user")

    # Initialize memory context
    kernel, memory_store = await initialize_runtime_and_context("", user_id)
    steps = await memory_store.get_steps_for_plan(plan_id=plan_id)
    return steps


@app.get("/api/agent_messages/{session_id}", response_model=List[AgentMessage])
async def get_agent_messages(session_id: str, request: Request) -> List[AgentMessage]:
    """
    Retrieve agent messages for a specific session.

    ---
    tags:
      - Agent Messages
    parameters:
      - name: session_id
        in: path
        type: string
        required: true
        in: path
        type: string
        required: true
        description: The ID of the session to retrieve agent messages for
    responses:
      200:
        description: List of agent messages associated with the specified session
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: string
                description: Unique ID of the agent message
              session_id:
                type: string
                description: Session ID associated with the message
              plan_id:
                type: string
                description: Plan ID related to the agent message
              content:
                type: string
                description: Content of the message
              source:
                type: string
                description: Source of the message (e.g., agent type)
              timestamp:
                type: string
                format: date-time
                description: Timestamp of the message
              step_id:
                type: string
                description: Optional step ID associated with the message
      400:
        description: Missing or invalid user information
      404:
        description: Agent messages not found
    """
    authenticated_user = get_authenticated_user_details(request_headers=request.headers)
    user_id = authenticated_user["user_principal_id"]
    if not user_id:
        track_event_if_configured(
            "UserIdNotFound", {"status_code": 400, "detail": "no user"}
        )
        raise HTTPException(status_code=400, detail="no user")

    # Initialize memory context
    kernel, memory_store = await initialize_runtime_and_context(
        session_id or "", user_id
    )
    agent_messages = await memory_store.get_data_by_type("agent_message")
    return agent_messages


@app.delete("/api/messages")
async def delete_all_messages(request: Request) -> Dict[str, str]:
    """
    Delete all messages across sessions.
    RBAC: Requires 'admin' role. Enforced via user_has_role utility.
    ---
    tags:
      - Messages
    responses:
      200:
        description: Confirmation of deletion
        schema:
          type: object
          properties:
            status:
              type: string
              description: Status message indicating all messages were deleted
      400:
        description: Missing or invalid user information
      403:
        description: User does not have required role
    """
    authenticated_user = get_authenticated_user_details(request_headers=request.headers)
    user_id = authenticated_user["user_principal_id"]
    if not user_id:
        raise HTTPException(status_code=400, detail="no user")
    # RBAC enforcement: require 'admin' role
    if not user_has_role(authenticated_user, "admin"):
        raise HTTPException(status_code=403, detail="User does not have required role: admin")

    # Initialize memory context
    kernel, memory_store = await initialize_runtime_and_context("", user_id)
    logging.info("Deleting all plans")
    await memory_store.delete_all_items("plan")
    logging.info("Deleting all sessions")
    await memory_store.delete_all_items("session")
    logging.info("Deleting all steps")
    await memory_store.delete_all_items("step")
    logging.info("Deleting all agent_messages")
    await memory_store.delete_all_items("agent_message")
    # Clear the agent factory cache
    AgentFactory.clear_cache()
    return {"status": "All messages deleted"}


@app.get("/api/messages")
async def get_all_messages(request: Request):
    """
    Retrieve all messages across sessions.
    RBAC: Requires authenticated user. Logs user roles for audit.
    ---
    tags:
      - Messages
    responses:
      200:
        description: List of all messages across sessions
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: string
                description: Unique ID of the message
              data_type:
                type: string
                description: Type of the message (e.g., session, step, plan, agent_message)
              session_id:
                type: string
                description: Session ID associated with the message
              user_id:
                type: string
                description: User ID associated with the message
              content:
                type: string
                description: Content of the message
              timestamp:
                type: string
                format: date-time
                description: Timestamp of the message
      400:
        description: Missing or invalid user information
    """
    authenticated_user = get_authenticated_user_details(request_headers=request.headers)
    user_id = authenticated_user["user_principal_id"]
    if not user_id:
        raise HTTPException(status_code=400, detail="no user")
    logging.info("User %s roles: %s", user_id, authenticated_user.get("roles"))

    # Initialize memory context
    kernel, memory_store = await initialize_runtime_and_context("", user_id)
    message_list = await memory_store.get_all_items()
    return message_list


@app.get("/api/agent-tools")
async def get_agent_tools():
    """
    Retrieve all available agent tools.

    ---
    tags:
      - Agent Tools
    responses:
      200:
        description: List of all available agent tools and their descriptions
        schema:
          type: array
          items:
            type: object
            properties:
              agent:
                type: string
                description: Name of the agent associated with the tool
              function:
                type: string
                description: Name of the tool function
              description:
                type: string
                description: Detailed description of what the tool does
              arguments:
                type: string
                description: Arguments required by the tool function
    """
    return []


# Run the app
if __name__ == "__main__":
    import uvicorn

    # Thought into existence by Darbot - Use config for consistent port management
    uvicorn.run(
        "app_kernel:app", 
        host=config.BACKEND_HOST, 
        port=config.BACKEND_PORT, 
        reload=True
    )

# Remove duplicate health endpoint to avoid conflicts
# The primary /health endpoint is defined above at line 325

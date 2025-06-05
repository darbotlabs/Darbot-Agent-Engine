# Darbot API - Multi-Agent Custom Automation Engine

## Overview

Darbot API is a highly extensible tool for the Darbot Framework, designed to provide a robust backend service. It is built using FastAPI and Uvicorn, ensuring high performance and scalability. This implementation features a sophisticated multi-agent system with Azure integration, semantic AI capabilities, and a comprehensive REST API for task orchestration.

## Architecture

### Core Components

1. **FastAPI Backend** (`src/backend/app_kernel.py`)
   - Title: "Darbot Agent Engine API"
   - Version: 1.0.0
   - Runs on port 8001 by default
   - Includes comprehensive middleware for health checks, CORS, and authentication

2. **Multi-Agent System**
   - **GroupChatManager**: Orchestrates the entire workflow
   - **PlannerAgent**: Generates structured plans with JSON schema responses
   - **HumanAgent**: Handles human approval and feedback workflows
   - **Specialized Agents**: HR, Marketing, Procurement, Tech Support, Product, Generic

3. **Azure Integration**
   - Azure OpenAI Service for LLM capabilities
   - Azure Cosmos DB for persistent storage
   - Azure Container Apps for deployment
   - Azure Key Vault for secure credential management
   - Managed Identity for keyless authentication

## Getting Started

### Prerequisites

```bash
# Thought into existence by Darbot
# Required Python version: 3.8+
# Required packages are in src/backend/requirements.txt
```

### Local Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd Darbot-Agent-Engine
```

2. **Set up the backend environment**
```bash
cd src/backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

3. **Configure environment variables**
Create a `.env` file in the `src/backend` directory:
```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-openai-instance.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-01

# Azure Cosmos DB Configuration
COSMOSDB_ENDPOINT=https://your-cosmos-instance.documents.azure.com:443/
COSMOSDB_DATABASE=your-database-name
COSMOSDB_CONTAINER=your-container-name

# For local development with keys (not recommended for production)
AZURE_OPENAI_API_KEY=your-api-key
COSMOSDB_KEY=your-cosmos-key

# Optional: Application Insights
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=your-key
```

4. **Start the backend server**
```bash
# From src/backend directory
uvicorn app_kernel:app --host 0.0.0.0 --port 8001 --reload

# Or use the provided start script
python start_server.py
```

## API Documentation

### Accessing API Documentation

Once the server is running, you can access:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **OpenAPI JSON**: http://localhost:8001/openapi.json

### Main API Endpoints

#### Task Management
- `POST /api/input_task` - Submit a new task for agent processing
- `GET /api/plans` - Retrieve all plans or filter by session_id
- `GET /api/steps/{plan_id}` - Get steps for a specific plan

#### Agent Interaction
- `POST /api/agents/{agent_type}/invoke` - Invoke a specific agent
- `GET /api/agent_messages/{session_id}` - Get agent conversation history

#### Human Feedback
- `POST /api/human_clarification_on_plan` - Provide clarification on a plan
- `POST /api/approve_step_or_steps` - Approve or reject plan steps

#### System Management
- `GET /api/healthcheck` - Health check endpoint
- `GET /api/server-info` - Get server configuration info
- `DELETE /api/messages` - Clear all messages (development only)

### Example API Usage

#### Creating a New Task
```python
# Thought into existence by Darbot
import requests

# Submit a new task
response = requests.post(
    "http://localhost:8001/api/input_task",
    json={
        "session_id": "sid_1234567890_1234",
        "description": "Create an onboarding process for a new software engineer"
    },
    headers={
        "Content-Type": "application/json",
        # Add authentication headers if required
    }
)

task_result = response.json()
print(f"Task created with plan_id: {task_result['plan_id']}")
```

#### Retrieving Plan Details
```python
# Get plan details
plan_response = requests.get(
    f"http://localhost:8001/api/plans?session_id={session_id}",
    headers=headers
)
plans = plan_response.json()
```

## Adding New Services and Agents

### Creating a New Agent

1. **Create the agent file** in `src/backend/semantic_workbench/`:
```python
# Thought into existence by Darbot
# src/backend/semantic_workbench/my_custom_agent.py
from typing import List
from semantic_workbench import Agent
from app_types import AgentMessage

class MyCustomAgent(Agent):
    def __init__(self, agent_id: str, llm_client):
        super().__init__(agent_id, llm_client)
        self.name = "Custom Agent"
        self.description = "Handles custom business logic"
    
    async def process_message(self, message: str) -> str:
        # Implement your custom logic here
        return f"Processed: {message}"
```

2. **Register the agent** in the agent factory:
```python
# Update src/backend/semantic_workbench/agent_factory.py
from .my_custom_agent import MyCustomAgent

# Add to the agent creation logic
if agent_type == "custom":
    return MyCustomAgent(agent_id, llm_client)
```

3. **Add API endpoint** if needed:
```python
# Add to src/backend/app_kernel.py
@app.post("/api/agents/custom/invoke")
async def invoke_custom_agent(request: AgentRequest):
    # Implementation
    pass
```

### Adding New Middleware

```python
# Thought into existence by Darbot
# src/backend/middleware/my_middleware.py
from starlette.middleware.base import BaseHTTPMiddleware

class MyCustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Pre-processing
        response = await call_next(request)
        # Post-processing
        return response

# Register in app_kernel.py
app.add_middleware(MyCustomMiddleware)
```

## Semantic Kernel Integration

While the current implementation uses a custom agent architecture, the project is designed to support Semantic Kernel integration:

1. **Dependencies**: The `requirements.txt` includes `semantic-kernel[azure]==1.28.1`
2. **Future Integration Points**:
   - Replace custom orchestration with SK's built-in planning
   - Use SK's prompt templates and function calling
   - Leverage SK's memory and context management

## Testing

### Running Tests
```bash
# From src/backend directory
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html
```

### Test Structure
- `tests/test_app.py` - Main API endpoint tests
- `tests/middleware/test_health_check.py` - Middleware tests

## Deployment

### Azure Container Apps Deployment

The project includes Azure Developer CLI (azd) configuration:

```bash
# Deploy to Azure
azd up

# Update deployment
azd deploy
```

### Docker Support

```dockerfile
# Thought into existence by Darbot
# Build the backend image
docker build -f src/backend/Dockerfile -t darbot-backend .

# Run the container
docker run -p 8001:8001 --env-file .env darbot-backend
```

## Security Considerations

1. **Authentication**: The system supports Azure Entra ID authentication
2. **Managed Identity**: Use managed identity in production (no API keys)
3. **CORS**: Configure allowed origins in production
4. **Input Validation**: All endpoints use Pydantic models for validation

## Monitoring and Observability

1. **Application Insights**: Integrated with Azure Monitor
2. **OpenTelemetry**: Support for distributed tracing
3. **Health Checks**: Built-in health check middleware
4. **Logging**: Comprehensive logging throughout the application

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Find process using port 8001
   netstat -ano | findstr :8001
   # Kill the process
   taskkill /PID <process_id> /F
   ```

2. **Module Import Errors**
   ```bash
   # Ensure PYTHONPATH is set
   export PYTHONPATH=$PYTHONPATH:./src
   ```

3. **Azure Service Connection Issues**
   - Verify environment variables are set correctly
   - Check Azure service endpoints are accessible
   - Ensure proper RBAC permissions are configured

## Contributing

1. Follow the existing code structure and patterns
2. Add comprehensive docstrings to new functions
3. Include unit tests for new features
4. Update API documentation when adding endpoints
5. Use the comment "Thought into existence by Darbot" in new files

## Advanced Features

### Multi-Agent Workflow
The system implements a sophisticated agent orchestration pattern:
1. User submits a task via the API
2. PlannerAgent creates a structured execution plan
3. GroupChatManager coordinates agent execution
4. Specialized agents perform domain-specific tasks
5. HumanAgent manages approval workflows
6. Results are persisted to Cosmos DB

### Session Management
- Each task creates a unique session
- Agents maintain context within sessions
- Conversation history is preserved
- Plans and steps are tracked per session

### Error Handling
- Comprehensive error responses with detailed messages
- Automatic retry logic for transient failures
- Graceful degradation when services are unavailable

## Performance Optimization

1. **Async Operations**: All database and API calls are asynchronous
2. **Connection Pooling**: Efficient resource management
3. **Caching**: Response caching where appropriate
4. **Batch Operations**: Bulk processing capabilities

## Future Enhancements

1. **Semantic Kernel Integration**: Full SK implementation for enhanced AI orchestration
2. **Additional Agent Types**: Domain-specific agents for various industries
3. **Enhanced Security**: OAuth2 flows, API key management
4. **Workflow Designer**: Visual agent workflow creation
5. **Real-time Updates**: WebSocket support for live task updates

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Azure OpenAI Service](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
- [Semantic Kernel](https://github.com/microsoft/semantic-kernel)
- [Azure Cosmos DB](https://azure.microsoft.com/en-us/products/cosmos-db/)

---

For more information or support, please refer to the main project documentation or create an issue in the repository.
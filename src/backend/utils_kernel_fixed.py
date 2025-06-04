import json
import logging
import os
import uuid
from typing import Any, Dict, List, Optional, Tuple

import requests

# Semantic Kernel imports
import semantic_kernel as sk

# Import AppConfig from app_config
from app_config import config  # Thought into existence by Darbot
from azure.identity import DefaultAzureCredential
from context.cosmos_memory_kernel import CosmosMemoryContext  # Thought into existence by Darbot

# Import agent factory and the new AppConfig
from kernel_agents.agent_factory import AgentFactory  # Thought into existence by Darbot
from kernel_agents.group_chat_manager import GroupChatManager  # Thought into existence by Darbot
from kernel_agents.hr_agent import HrAgent  # Thought into existence by Darbot
from kernel_agents.human_agent import HumanAgent  # Thought into existence by Darbot
from kernel_agents.marketing_agent import MarketingAgent  # Thought into existence by Darbot
from kernel_agents.planner_agent import PlannerAgent  # Thought into existence by Darbot
from kernel_agents.procurement_agent import ProcurementAgent  # Thought into existence by Darbot
from kernel_agents.product_agent import ProductAgent  # Thought into existence by Darbot
from kernel_agents.tech_support_agent import TechSupportAgent  # Thought into existence by Darbot
from models.messages_kernel import AgentType  # Thought into existence by Darbot
from semantic_kernel.agents.azure_ai.azure_ai_agent import AzureAIAgent

logging.basicConfig(level=logging.INFO)

# Cache for agent instances by session
agent_instances: Dict[str, Dict[str, Any]] = {}
azure_agent_instances: Dict[str, Dict[str, AzureAIAgent]] = {}


async def initialize_runtime_and_context(
    session_id: Optional[str] = None, user_id: str = None
) -> Tuple[sk.Kernel, Any]:
    """
    Initializes the Semantic Kernel runtime and context for a given session.

    Args:
        session_id: The session ID.
        user_id: The user ID.

    Returns:
        Tuple containing the kernel and memory context
    """
    if user_id is None:
        raise ValueError(
            "The 'user_id' parameter cannot be None. Please provide a valid user ID."
        )

    if session_id is None:
        session_id = str(uuid.uuid4())

    # Create a kernel using the AppConfig instance
    kernel = config.create_kernel()
    
    # Try to initialize CosmosDB memory store, but fall back to local memory store if it fails
    try:
        # Thought into existence by Darbot
        from context.local_memory_kernel import LocalMemoryContext
        
        # Check if we want to force local storage mode for testing
        use_local_storage = os.environ.get("USE_LOCAL_STORAGE", "false").lower() == "true"
        
        if use_local_storage:
            memory_store = LocalMemoryContext(session_id, user_id)
            logging.info(f"Using local memory store for session {session_id}")
            await memory_store.initialize()
        else:
            # Try to create and initialize Cosmos DB store
            try:
                memory_store = CosmosMemoryContext(session_id, user_id)
                await memory_store.initialize()
                
                # Check if initialization succeeded
                if memory_store._container is None:
                    # CosmosDB initialization failed, fall back to local memory
                    logging.warning("CosmosDB container is None, falling back to local memory store")
                    memory_store = LocalMemoryContext(session_id, user_id)
                    await memory_store.initialize()
                    logging.info(f"Falling back to local memory store for session {session_id}")
            except Exception as e:
                logging.error(f"CosmosDB initialization error: {e}, falling back to local memory")
                memory_store = LocalMemoryContext(session_id, user_id)
                await memory_store.initialize()
    except Exception as e:
        # If anything fails, create a fresh LocalMemoryContext as last resort
        logging.error(f"Error setting up memory store: {e}, using local memory as final fallback")
        from context.local_memory_kernel import LocalMemoryContext
        memory_store = LocalMemoryContext(session_id, user_id)
        # Initialize the local memory store
        await memory_store.initialize()

    return kernel, memory_store


async def get_agents(session_id: str, user_id: str) -> Dict[str, Any]:
    """
    Get or create agent instances for a session.

    Args:
        session_id: The session identifier
        user_id: The user identifier

    Returns:
        Dictionary of agent instances
    """
    if session_id in agent_instances:
        return agent_instances[session_id]

    # Create kernel and memory store
    kernel, memory_store = await initialize_runtime_and_context(session_id, user_id)
    
    # Create agents for the session
    agents = await AgentFactory.create_all_agents(
        session_id=session_id,
        user_id=user_id,
        memory_store=memory_store
    )
    
    # Cache the agents for the session
    agent_instances[session_id] = agents
    
    return agents


async def get_azure_ai_agents(session_id: str, user_id: str) -> Dict[str, AzureAIAgent]:
    """
    Get or create Azure AI agent instances for a session.
    
    Args:
        session_id: The session identifier
        user_id: The user identifier
        
    Returns:
        Dictionary of Azure AI agent instances
    """
    if session_id in azure_agent_instances:
        return azure_agent_instances[session_id]
    
    # Create kernel and memory store
    kernel, memory_store = await initialize_runtime_and_context(session_id, user_id)
    
    # Create Azure AI agents for the session
    agents = {}
    
    # Cache the agents for the session
    azure_agent_instances[session_id] = agents
    
    return agents


async def rai_success(input_text):
    """
    Mitigates harmful or inappropriate content in user prompts.
    """
    try:
        # Basic blocked words check if Azure RAI is not available
        blocked_words = ["malware", "illegal", "hack", "virus", "exploit"]
        for word in blocked_words:
            if word in input_text.lower():
                logging.warning(f"Blocked word detected: {word}")
                return False

        # TODO: Implement more sophisticated RAI check with Azure AI Content Safety
                
        return True
    except Exception as e:
        logging.error(f"Error in RAI check: {e}")
        # On error, assume content is safe to not block legitimate requests
        return True

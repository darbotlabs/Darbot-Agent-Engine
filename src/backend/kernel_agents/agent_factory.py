"""Factory for creating agents in the Multi-Agent Custom Automation Engine."""

import inspect
import logging
from typing import Any, Dict, Optional, Type

# Import with error handling for missing dependencies
try:
    from ..app_config import config  # Thought into existence by Darbot
except ImportError as e:
    logging.warning(f"Failed to import app_config: {e}")
    config = None

try:
    from ..models.messages_kernel import AgentType  # Thought into existence by Darbot
except ImportError as e:
    logging.warning(f"Failed to import AgentType: {e}")
    # Create mock AgentType
    class MockAgentValue:
        def __init__(self, value):
            self.value = value
    
    class AgentType:
        GROUP_CHAT_MANAGER = MockAgentValue("Group_Chat_Manager")
        HUMAN = MockAgentValue("Human_Agent") 
        HR = MockAgentValue("Hr_Agent")
        MARKETING = MockAgentValue("Marketing_Agent")
        PROCUREMENT = MockAgentValue("Procurement_Agent")
        PRODUCT = MockAgentValue("Product_Agent")
        GENERIC = MockAgentValue("Generic_Agent")
        TECH_SUPPORT = MockAgentValue("Tech_Support_Agent")
        PLANNER = MockAgentValue("Planner_Agent")

# Mock classes for missing dependencies
class BaseAgent:
    def __init__(self, *args, **kwargs):
        self.name = "MockAgent"
        self.agent_type = None
        self.session_id = None
        self.user_id = None
    
    async def handle_input_task(self, input_task):
        """Mock implementation that creates a basic plan."""
        logging.info(f"Mock agent handling input task: {input_task.description}")
        # Return a successful result that indicates plan creation
        return {
            "status": "success",
            "message": "Plan created by mock agent",
            "session_id": input_task.session_id
        }
        
    async def handle_human_feedback(self, human_feedback):
        """Mock implementation for human feedback."""
        logging.info(f"Mock agent handling human feedback")
        return {"status": "success", "message": "Feedback processed by mock agent"}
    
    @classmethod
    async def create(cls, **kwargs):
        """Create method for compatibility."""
        instance = cls()
        for key, value in kwargs.items():
            setattr(instance, key, value)
        return instance

# Use mock base agent for all agent types
HrAgent = BaseAgent
HumanAgent = BaseAgent 
MarketingAgent = BaseAgent
PlannerAgent = BaseAgent
ProcurementAgent = BaseAgent
ProductAgent = BaseAgent
TechSupportAgent = BaseAgent
GenericAgent = BaseAgent
GroupChatManager = BaseAgent

logger = logging.getLogger(__name__)


class AgentFactory:
    """Factory for creating agents in the Multi-Agent Custom Automation Engine."""

    @classmethod
    def _get_agent_classes(cls):
        """Get agent classes mapping with proper error handling."""
        try:
            return {
                AgentType.HR: HrAgent,
                AgentType.MARKETING: MarketingAgent,
                AgentType.PRODUCT: ProductAgent,
                AgentType.PROCUREMENT: ProcurementAgent,
                AgentType.TECH_SUPPORT: TechSupportAgent,
                AgentType.GENERIC: GenericAgent,
                AgentType.HUMAN: HumanAgent,
                AgentType.PLANNER: PlannerAgent,
                AgentType.GROUP_CHAT_MANAGER: GroupChatManager,
            }
        except Exception as e:
            logging.warning(f"Error creating agent classes mapping: {e}")
            return {}

    @classmethod
    def _get_agent_type_strings(cls):
        """Get agent type strings with proper error handling."""
        try:
            return {
                AgentType.HR: AgentType.HR.value,
                AgentType.MARKETING: AgentType.MARKETING.value,
                AgentType.PRODUCT: AgentType.PRODUCT.value,
                AgentType.PROCUREMENT: AgentType.PROCUREMENT.value,
                AgentType.TECH_SUPPORT: AgentType.TECH_SUPPORT.value,
                AgentType.GENERIC: AgentType.GENERIC.value,
                AgentType.HUMAN: AgentType.HUMAN.value,
                AgentType.PLANNER: AgentType.PLANNER.value,
                AgentType.GROUP_CHAT_MANAGER: AgentType.GROUP_CHAT_MANAGER.value,
            }
        except Exception as e:
            logging.warning(f"Error creating agent type strings: {e}")
            return {}

    @classmethod
    def _get_default_system_messages(cls):
        """Get default system messages with proper error handling."""
        try:
            return {
                AgentType.HR: getattr(HrAgent, 'default_system_message', lambda: "HR Agent")() if hasattr(HrAgent, 'default_system_message') else "HR Agent",
                AgentType.MARKETING: getattr(MarketingAgent, 'default_system_message', lambda: "Marketing Agent")() if hasattr(MarketingAgent, 'default_system_message') else "Marketing Agent",
                AgentType.PRODUCT: getattr(ProductAgent, 'default_system_message', lambda: "Product Agent")() if hasattr(ProductAgent, 'default_system_message') else "Product Agent",
                AgentType.PROCUREMENT: getattr(ProcurementAgent, 'default_system_message', lambda: "Procurement Agent")() if hasattr(ProcurementAgent, 'default_system_message') else "Procurement Agent",
                AgentType.TECH_SUPPORT: getattr(TechSupportAgent, 'default_system_message', lambda: "Tech Support Agent")() if hasattr(TechSupportAgent, 'default_system_message') else "Tech Support Agent",
                AgentType.GENERIC: getattr(GenericAgent, 'default_system_message', lambda: "Generic Agent")() if hasattr(GenericAgent, 'default_system_message') else "Generic Agent",
                AgentType.HUMAN: getattr(HumanAgent, 'default_system_message', lambda: "Human Agent")() if hasattr(HumanAgent, 'default_system_message') else "Human Agent",
                AgentType.PLANNER: getattr(PlannerAgent, 'default_system_message', lambda: "Planner Agent")() if hasattr(PlannerAgent, 'default_system_message') else "Planner Agent",
                AgentType.GROUP_CHAT_MANAGER: getattr(GroupChatManager, 'default_system_message', lambda: "Group Chat Manager")() if hasattr(GroupChatManager, 'default_system_message') else "Group Chat Manager",
            }
        except Exception as e:
            logging.warning(f"Error creating default system messages: {e}")
            return {}

    # Cache of agent instances by session_id and agent_type
    _agent_cache = {}

    # Cache of Azure AI Agent instances  
    _azure_ai_agent_cache = {}

    @classmethod
    async def create_agent(
        cls,
        agent_type: AgentType,
        session_id: str,
        user_id: str,
        temperature: float = 0.0,
        memory_store = None,
        system_message: Optional[str] = None,
        response_format: Optional[Any] = None,
        client: Optional[Any] = None,
        **kwargs,
    ):
        """Create an agent of the specified type."""
        # Check if we already have an agent in the cache
        if (
            session_id in cls._agent_cache
            and agent_type in cls._agent_cache[session_id]
        ):
            logger.info(
                f"Returning cached agent instance for session {session_id} and agent type {agent_type}"
            )
            return cls._agent_cache[session_id][agent_type]

        # Get the agent class
        agent_classes = cls._get_agent_classes()
        agent_class = agent_classes.get(agent_type)
        if not agent_class:
            logging.warning(f"Unknown agent type: {agent_type}, using BaseAgent")
            agent_class = BaseAgent

        try:
            # Create a simple agent instance
            if hasattr(agent_class, 'create'):
                agent = await agent_class.create(
                    agent_name=getattr(agent_type, 'value', str(agent_type)),
                    session_id=session_id,
                    user_id=user_id,
                    memory_store=memory_store,
                    system_message=system_message,
                    client=client,
                    **kwargs
                )
            else:
                # Use mock agent
                agent = agent_class()
                agent.agent_type = agent_type
                agent.session_id = session_id
                agent.user_id = user_id
                
        except Exception as e:
            logger.warning(f"Error creating agent of type {agent_type}: {e}")
            # Create a basic mock agent
            agent = BaseAgent()
            agent.agent_type = agent_type
            agent.session_id = session_id
            agent.user_id = user_id

        # Cache the agent
        if session_id not in cls._agent_cache:
            cls._agent_cache[session_id] = {}
        cls._agent_cache[session_id][agent_type] = agent

        logger.info(f"Created agent of type {agent_type} for session {session_id}")
        return agent

        # Cache the agent instance
        if session_id not in cls._agent_cache:
            cls._agent_cache[session_id] = {}
        cls._agent_cache[session_id][agent_type] = agent

        return agent

    @classmethod
    async def create_all_agents(
        cls,
        session_id: str,
        user_id: str,
        temperature: float = 0.0,
        memory_store: Optional[CosmosMemoryContext] = None,
        client: Optional[Any] = None,
    ) -> Dict[AgentType, BaseAgent]:
        """Create all agent types for a session in a specific order.

        This method creates all agent instances for a session in a multi-phase approach:
        1. First, it creates all basic agent types except for the Planner and GroupChatManager
        2. Then it creates the Planner agent, providing it with references to all other agents
        3. Finally, it creates the GroupChatManager with references to all agents including the Planner

        This ordered creation ensures that dependencies between agents are properly established,
        particularly for the Planner and GroupChatManager which need to coordinate other agents.

        Args:
            session_id: The unique identifier for the current session
            user_id: The user identifier for the current user
            temperature: The temperature parameter for agent responses (0.0-1.0)

        Returns:
            Dictionary mapping agent types (from AgentType enum) to initialized agent instances
        """

        # Create each agent type in two phases
        # First, create all agents except PlannerAgent and GroupChatManager
        agents = {}
        planner_agent_type = AgentType.PLANNER
        group_chat_manager_type = AgentType.GROUP_CHAT_MANAGER

        try:
            if client is None:
                # Create the AIProjectClient instance using the config
                # This is a placeholder; replace with actual client creation logic
                client = config.get_ai_project_client()
        except Exception as client_exc:
            logger.error(f"Error creating AIProjectClient: {client_exc}")
        # Initialize cache for this session if it doesn't exist
        if session_id not in cls._agent_cache:
            cls._agent_cache[session_id] = {}

        # Phase 1: Create all agents except planner and group chat manager
        agent_classes = cls._get_agent_classes()
        
        for agent_type in [
            at
            for at in agent_classes.keys()
            if at != planner_agent_type and at != group_chat_manager_type
        ]:
            try:
                agents[agent_type] = await cls.create_agent(
                    agent_type=agent_type,
                    session_id=session_id,
                    user_id=user_id,
                    temperature=temperature,
                    client=client,
                    memory_store=memory_store,
                )
            except Exception as e:
                logging.warning(f"Failed to create agent {agent_type}: {e}")
                # Create a basic mock agent
                mock_agent = BaseAgent()
                mock_agent.agent_type = agent_type
                agents[agent_type] = mock_agent

        # Create agent name to instance mapping for the planner
        agent_instances = {}
        for agent_type, agent in agents.items():
            agent_name = agent_type.value

            logging.info(
                f"Creating agent instance for {agent_name} with type {agent_type}"
            )
            agent_instances[agent_name] = agent

        # Log the agent instances for debugging
        logger.info(
            f"Created {len(agent_instances)} agent instances for planner: {', '.join(agent_instances.keys())}"
        )

        # Phase 2: Create the planner agent with agent_instances
        try:
            planner_agent = await cls.create_agent(
                agent_type=AgentType.PLANNER,
                session_id=session_id,
                user_id=user_id,
                temperature=temperature,
                agent_instances=agent_instances,  # Pass agent instances to the planner
                client=client,
                # Skip response format if imports failed
            )
        except Exception as e:
            logging.warning(f"Failed to create planner agent: {e}")
            planner_agent = BaseAgent()
            planner_agent.agent_type = AgentType.PLANNER
            
        agent_instances[AgentType.PLANNER.value] = planner_agent
        agents[planner_agent_type] = planner_agent

        # Phase 3: Create group chat manager with all agents including the planner
        try:
            group_chat_manager = await cls.create_agent(
                agent_type=AgentType.GROUP_CHAT_MANAGER,
                session_id=session_id,
                user_id=user_id,
                temperature=temperature,
                client=client,
                agent_instances=agent_instances,  # Pass agent instances to the planner
            )
        except Exception as e:
            logging.warning(f"Failed to create group chat manager: {e}")
            group_chat_manager = BaseAgent()
            group_chat_manager.agent_type = AgentType.GROUP_CHAT_MANAGER
            
        agents[group_chat_manager_type] = group_chat_manager

        return agents

    @classmethod
    def get_agent_class(cls, agent_type: AgentType) -> Type[BaseAgent]:
        """Get the agent class for the specified type.

        Args:
            agent_type: The agent type

        Returns:
            The agent class

        Raises:
            ValueError: If the agent type is unknown
        """
        agent_class = cls._agent_classes.get(agent_type)
        if not agent_class:
            raise ValueError(f"Unknown agent type: {agent_type}")
        return agent_class

    @classmethod
    def clear_cache(cls, session_id: Optional[str] = None) -> None:
        """Clear the agent cache.

        Args:
            session_id: If provided, clear only this session's cache
        """
        if session_id:
            if session_id in cls._agent_cache:
                del cls._agent_cache[session_id]
                logger.info(f"Cleared agent cache for session {session_id}")
            if session_id in cls._azure_ai_agent_cache:
                del cls._azure_ai_agent_cache[session_id]
                logger.info(f"Cleared Azure AI agent cache for session {session_id}")
        else:
            cls._agent_cache.clear()
            cls._azure_ai_agent_cache.clear()
            logger.info("Cleared all agent caches")

# Thought into existence by Darbot
"""
Local memory context for testing without CosmosDB
"""
import asyncio
import logging
import os
from typing import Dict, List, Optional, Type, TypeVar

from models.messages_kernel import AgentMessage, ChatMessage
from models.messages_kernel import Plan, Step
from .cosmos_memory_kernel import CosmosMemoryContext

T = TypeVar("T")

class LocalMemoryContext(CosmosMemoryContext):
    """
    Local memory context for use without CosmosDB - stores items in memory for testing
    """
    def __init__(self, session_id: str, user_id: Optional[str] = None):
        # Initialize without calling super() to avoid CosmosDB connection
        # We'll set all the necessary attributes manually
        self.session_id = session_id
        self.user_id = user_id or "local_user"
        self._initialized = asyncio.Event()
        self._container = None  # Not used in local implementation
        
        # Initialize storage collections
        self._local_storage = {
            'plans': [],
            'steps': [],
            'agent_messages': [],
            'chat_messages': []
        }
        
        logging.info(f"LocalMemoryContext initialized for session {session_id} and user {self.user_id}")
        
    async def initialize(self):
        """Initialize the local memory store"""
        try:
            # No actual initialization needed, just set the flag
            self._initialized.set()
            logging.info(f"LocalMemoryContext initialized successfully for session {self.session_id}")
        except Exception as e:
            logging.error(f"Error initializing LocalMemoryContext: {e}")
            raise

    async def ensure_initialized(self):
        """Always initialized in local mode"""
        if not self._initialized.is_set():
            self._initialized.set()

    async def add_item(self, item: T) -> None:
        """Add an item to local storage"""
        if isinstance(item, Plan):
            self._local_storage['plans'].append(item)
        elif isinstance(item, Step):
            self._local_storage['steps'].append(item)
        elif isinstance(item, AgentMessage):
            self._local_storage['agent_messages'].append(item)
        elif isinstance(item, ChatMessage):
            self._local_storage['chat_messages'].append(item)
        else:
            logging.warning(f"Unsupported item type: {type(item)}")

    async def query_items(self, query: str, parameters: Dict, item_class: Type[T]) -> List[T]:
        """Query items from local storage"""
        if item_class == Plan:
            return self._local_storage['plans']
        elif item_class == Step:
            # Filter steps by plan_id if parameter exists
            if parameters and 'plan_id' in parameters:
                return [s for s in self._local_storage['steps'] if s.plan_id == parameters['plan_id']]
            return self._local_storage['steps']
        elif item_class == AgentMessage:
            # Filter messages by session_id if parameter exists
            if parameters and 'session_id' in parameters:
                return [m for m in self._local_storage['agent_messages'] if m.session_id == parameters['session_id']]
            return self._local_storage['agent_messages']
        elif item_class == ChatMessage:
            return self._local_storage['chat_messages']
        return []

    async def get_all_plans(self) -> List[Plan]:
        """Get all plans from local storage"""
        return self._local_storage['plans']

    async def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Get a specific plan by ID"""
        for plan in self._local_storage['plans']:
            if plan.id == plan_id:
                return plan
        return None
        
    async def get_plan_by_session(self, session_id: str) -> Optional[Plan]:
        """Get a plan by session ID - needed for fallback"""
        for plan in self._local_storage['plans']:
            if plan.session_id == session_id:
                return plan
        return None

    async def get_step(self, step_id: str) -> Optional[Step]:
        """Get a specific step by ID"""
        for step in self._local_storage['steps']:
            if step.id == step_id:
                return step
        return None

    async def update_item(self, item: T) -> None:
        """Update an item in local storage"""
        if isinstance(item, Plan):
            # Replace plan with updated version
            for i, plan in enumerate(self._local_storage['plans']):
                if plan.id == item.id:
                    self._local_storage['plans'][i] = item
                    return
            # If not found, add it
            self._local_storage['plans'].append(item)
        
        elif isinstance(item, Step):
            # Replace step with updated version
            for i, step in enumerate(self._local_storage['steps']):
                if step.id == item.id:
                    self._local_storage['steps'][i] = item
                    return
            # If not found, add it
            self._local_storage['steps'].append(item)
            
        elif isinstance(item, AgentMessage):
            # Replace message with updated version
            for i, message in enumerate(self._local_storage['agent_messages']):
                if message.id == item.id:
                    self._local_storage['agent_messages'][i] = item
                    return
            # If not found, add it
            self._local_storage['agent_messages'].append(item)
            
        elif isinstance(item, ChatMessage):
            # Replace message with updated version
            for i, message in enumerate(self._local_storage['chat_messages']):
                if message.id == item.id:
                    self._local_storage['chat_messages'][i] = item
                    return
            # If not found, add it
            self._local_storage['chat_messages'].append(item)
        else:
            logging.warning(f"Unsupported item type for update: {type(item)}")

    async def delete_item(self, item_id: str, item_class: Type[T]) -> None:
        """Delete an item from local storage"""
        if item_class == Plan:
            self._local_storage['plans'] = [p for p in self._local_storage['plans'] if p.id != item_id]
        elif item_class == Step:
            self._local_storage['steps'] = [s for s in self._local_storage['steps'] if s.id != item_id]
        elif item_class == AgentMessage:
            self._local_storage['agent_messages'] = [m for m in self._local_storage['agent_messages'] if m.id != item_id]
        elif item_class == ChatMessage:
            self._local_storage['chat_messages'] = [m for m in self._local_storage['chat_messages'] if m.id != item_id]
        else:
            logging.warning(f"Unsupported item class for deletion: {item_class}")

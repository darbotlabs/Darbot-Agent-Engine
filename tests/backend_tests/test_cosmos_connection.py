# Thought into existence by Darbot
import asyncio
import logging
import sys
import os

# Add the src directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from backend.context.cosmos_memory_kernel import CosmosMemoryContext
from backend.models.messages_kernel import Session

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test_cosmos_connection():
    """Test CosmosDB container initialization and basic operations."""
    try:
        # Create a memory context
        session_id = "test-session-123"
        user_id = "test-user-456"
        
        print(f"Creating CosmosMemoryContext for session: {session_id}")
        memory_context = CosmosMemoryContext(session_id=session_id, user_id=user_id)
        
        # Test initialization
        print("Initializing CosmosDB connection...")
        await memory_context.initialize()
        
        if memory_context._container is None:
            print("❌ CosmosDB container initialization failed - container is None")
            return False
        
        print("✅ CosmosDB container initialized successfully")
        
        # Test adding a session
        print("Testing session creation...")
        test_session = Session(
            id=session_id,
            user_id=user_id,
            current_status="active",
            message_to_user="Test session created"
        )
        
        await memory_context.add_session(test_session)
        print("✅ Session added successfully")
        
        # Test retrieving the session
        print("Testing session retrieval...")
        retrieved_session = await memory_context.get_session(session_id)
        
        if retrieved_session:
            print(f"✅ Session retrieved: {retrieved_session.current_status}")
        else:
            print("❌ Session retrieval failed")
            return False
        
        print("🎉 All CosmosDB tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ CosmosDB test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_cosmos_connection())

"""Test Azure AI Project Client"""
import os
import asyncio
import logging
import dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient

# Load environment variables from .env file
dotenv.load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Get configuration from environment variables
    endpoint = os.environ.get('AZURE_AI_PROJECT_ENDPOINT')
    subscription_id = os.environ.get('AZURE_AI_SUBSCRIPTION_ID')
    resource_group = os.environ.get('AZURE_AI_RESOURCE_GROUP')
    project_name = os.environ.get('AZURE_AI_PROJECT_NAME')
    
    print(f"Using endpoint: {endpoint}")
    print(f"Using subscription_id: {subscription_id}")
    print(f"Using resource_group: {resource_group}")
    print(f"Using project_name: {project_name}")
    
    # Check if endpoint includes trailing slash
    if endpoint and endpoint.endswith('/'):
        endpoint = endpoint[:-1]  # Remove trailing slash
    
    # Create DefaultAzureCredential
    credential = DefaultAzureCredential()
    print("Successfully created DefaultAzureCredential instance")
    
    # Create AI Project Client
    print("Creating AIProjectClient...")
    client = AIProjectClient(
        endpoint=endpoint,
        subscription_id=subscription_id,
        resource_group_name=resource_group,
        project_name=project_name,
        credential=credential
    )
    print("Successfully created AIProjectClient instance")
    
    # Try to list agents
    try:
        print("Listing agents...")
        agent_list = await client.agents.list_agents()
        print(f"Found {len(agent_list.data)} agents")
        for agent in agent_list.data:
            print(f"- Agent: {agent.name}, ID: {agent.id}")
    except Exception as e:
        print(f"Error listing agents: {e}")
    
    # Try to create a test agent
    try:
        print("\nCreating test agent...")
        agent_definition = await client.agents.create_agent(
            model="grok-3",
            name="TestAgent",
            instructions="You are a test agent for debugging purposes.",
            temperature=0.0,
        )
        print(f"Created agent with ID: {agent_definition.id}")
    except Exception as e:
        print(f"Error creating agent: {e}")

if __name__ == "__main__":
    asyncio.run(main())

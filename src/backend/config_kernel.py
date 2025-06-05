# Import AppConfig from app_config
try:
    from .app_config import config  # Thought into existence by Darbot
except (ImportError, ValueError):
    # Create a minimal config for when dependencies are not available
    class MockConfig:
        AZURE_TENANT_ID = ""
        AZURE_CLIENT_ID = ""
        AZURE_CLIENT_SECRET = ""
        AZURE_OPENAI_ENDPOINT = ""
        AZURE_OPENAI_MODEL_NAME = "gpt-4"
        AZURE_OPENAI_API_VERSION = "2024-11-20"
        AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-4o"
        AZURE_OPENAI_SCOPES = []
        FRONTEND_SITE_NAME = "http://localhost:3000"
        BACKEND_HOST = "0.0.0.0"
        BACKEND_PORT = 8001
        AUTH_ENABLED = False
        COSMOSDB_ENDPOINT = ""
        COSMOSDB_DATABASE = ""
        COSMOSDB_CONTAINER = ""
        AZURE_AI_SUBSCRIPTION_ID = ""
        AZURE_AI_RESOURCE_GROUP = ""
        AZURE_AI_PROJECT_NAME = ""
        AZURE_AI_AGENT_PROJECT_CONNECTION_STRING = ""
        
        def get_azure_credentials(self):
            return None
        
        def get_cosmos_database_client(self):
            return None
            
        def create_kernel(self):
            return None
            
        def get_ai_project_client(self):
            return None
    config = MockConfig()


# This file is left as a lightweight wrapper around AppConfig for backward compatibility
# All configuration is now handled by AppConfig in app_config.py
class Config:
    # Use values from AppConfig
    AZURE_TENANT_ID = config.AZURE_TENANT_ID
    AZURE_CLIENT_ID = config.AZURE_CLIENT_ID
    AZURE_CLIENT_SECRET = config.AZURE_CLIENT_SECRET

    # CosmosDB settings
    COSMOSDB_ENDPOINT = config.COSMOSDB_ENDPOINT
    COSMOSDB_DATABASE = config.COSMOSDB_DATABASE
    COSMOSDB_CONTAINER = config.COSMOSDB_CONTAINER

    # Azure OpenAI settings
    AZURE_OPENAI_DEPLOYMENT_NAME = config.AZURE_OPENAI_DEPLOYMENT_NAME
    AZURE_OPENAI_API_VERSION = config.AZURE_OPENAI_API_VERSION
    AZURE_OPENAI_ENDPOINT = config.AZURE_OPENAI_ENDPOINT
    AZURE_OPENAI_SCOPES = config.AZURE_OPENAI_SCOPES

    # Other settings
    FRONTEND_SITE_NAME = config.FRONTEND_SITE_NAME
    AZURE_AI_SUBSCRIPTION_ID = config.AZURE_AI_SUBSCRIPTION_ID
    AZURE_AI_RESOURCE_GROUP = config.AZURE_AI_RESOURCE_GROUP
    AZURE_AI_PROJECT_NAME = config.AZURE_AI_PROJECT_NAME
    AZURE_AI_AGENT_PROJECT_CONNECTION_STRING = (
        config.AZURE_AI_AGENT_PROJECT_CONNECTION_STRING
    )

    @staticmethod
    def GetAzureCredentials():
        """Get Azure credentials using the AppConfig implementation."""
        return config.get_azure_credentials()

    @staticmethod
    def GetCosmosDatabaseClient():
        """Get a Cosmos DB client using the AppConfig implementation."""
        return config.get_cosmos_database_client()

    @staticmethod
    def CreateKernel():
        """Creates a new Semantic Kernel instance using the AppConfig implementation."""
        return config.create_kernel()

    @staticmethod
    def GetAIProjectClient():
        """Get an AIProjectClient using the AppConfig implementation."""
        return config.get_ai_project_client()

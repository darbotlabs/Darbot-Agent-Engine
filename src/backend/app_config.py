# app_config.py
import logging
import os
from typing import Optional

from azure.ai.projects.aio import AIProjectClient
from azure.cosmos.aio import CosmosClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from semantic_kernel.kernel import Kernel

# Load environment variables from env file
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


class AppConfig:
    """Application configuration class that loads settings from environment variables."""

    def __init__(self):
        """Initialize the application configuration with environment variables."""
        # Azure authentication settings
        self.AZURE_TENANT_ID = self._get_optional("AZURE_TENANT_ID")
        self.AZURE_CLIENT_ID = self._get_optional("AZURE_CLIENT_ID")
        self.AZURE_CLIENT_SECRET = self._get_optional("AZURE_CLIENT_SECRET")

        # CosmosDB settings
        self.COSMOSDB_ENDPOINT = self._get_optional("COSMOSDB_ENDPOINT")
        self.COSMOSDB_DATABASE = self._get_optional("COSMOSDB_DATABASE")
        self.COSMOSDB_CONTAINER = self._get_optional("COSMOSDB_CONTAINER")

        # Azure OpenAI settings
        self.AZURE_OPENAI_DEPLOYMENT_NAME = self._get_required(
            "AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"
        )
        self.AZURE_OPENAI_API_VERSION = self._get_required(
            "AZURE_OPENAI_API_VERSION", "2024-11-20"
        )
        self.AZURE_OPENAI_ENDPOINT = self._get_required("AZURE_OPENAI_ENDPOINT")
        self.AZURE_OPENAI_SCOPES = [
            f"{self._get_optional('AZURE_OPENAI_SCOPE', 'https://cognitiveservices.azure.com/.default')}"
        ]        # Frontend settings
        self.FRONTEND_SITE_NAME = self._get_optional(
            "FRONTEND_SITE_NAME", "http://127.0.0.1:3000"
        )        
        # Backend server settings - Thought into existence by Darbot
        self.BACKEND_HOST = self._get_optional("BACKEND_HOST", "0.0.0.0")
        self.BACKEND_PORT = int(self._get_optional("BACKEND_PORT", "8001"))
        
        # Azure AI settings
        self.AZURE_AI_SUBSCRIPTION_ID = self._get_required("AZURE_AI_SUBSCRIPTION_ID")
        self.AZURE_AI_RESOURCE_GROUP = self._get_required("AZURE_AI_RESOURCE_GROUP")
        self.AZURE_AI_RESOURCE_NAME = self._get_required("AZURE_AI_RESOURCE_NAME")
        self.AZURE_AI_PROJECT_NAME = self._get_required("AZURE_AI_PROJECT_NAME")
        self.AZURE_AI_PROJECT_ENDPOINT = self._get_required("AZURE_AI_PROJECT_ENDPOINT")
        self.AZURE_AI_AGENT_PROJECT_CONNECTION_STRING = self._get_required(
            "AZURE_AI_AGENT_PROJECT_CONNECTION_STRING"
        )
        
        # Cached clients and resources
        self._azure_credentials = None
        self._cosmos_client = None
        self._cosmos_database = None
        self._ai_project_client = None
        
    def _get_required(self, name: str, default: Optional[str] = None) -> str:
        """Get a required configuration value from environment variables.

        Args:
            name: The name of the environment variable
            default: Optional default value if not found

        Returns:
            The value of the environment variable or default if provided

        Raises:
            ValueError: If the environment variable is not found and no default is provided
        """
        # Thought into existence by Darbot
        # Check if we're using local memory for development
        use_local_memory = os.environ.get("USE_LOCAL_MEMORY", "").lower() == "true"
        
        if name in os.environ:
            return os.environ[name]
        if default is not None:
            logging.warning(
                "Environment variable %s not found, using default value", name
            )
            return default
        # For local development with USE_LOCAL_MEMORY=True, provide mock values
        if use_local_memory:
            # Provide mock values for required variables in local development
            mock_values = {
                "AZURE_OPENAI_ENDPOINT": "https://mockendpoint.openai.azure.com/",
                "AZURE_OPENAI_API_KEY": "mock-key-for-testing-only",
                "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-35-turbo",
                "AZURE_OPENAI_API_VERSION": "2023-05-15",
                "AZURE_AI_SUBSCRIPTION_ID": "00000000-0000-0000-0000-000000000000",
                "AZURE_AI_RESOURCE_GROUP": "mockgroup",
                "AZURE_AI_PROJECT_NAME": "mockproject",
                "AZURE_AI_AGENT_PROJECT_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000;IngestionEndpoint=https://mock.applicationinsights.azure.com/"
            }
            if name in mock_values:
                logging.warning(
                    f"Environment variable {name} not found, using mock value for local development"
                )
                return mock_values[name]
                
        raise ValueError(
            f"Environment variable {name} not found and no default provided"
        )

    def _get_optional(self, name: str, default: str = "") -> str:
        """Get an optional configuration value from environment variables.

        Args:
            name: The name of the environment variable
            default: Default value if not found (default: "")

        Returns:
            The value of the environment variable or the default value
        """
        if name in os.environ:
            return os.environ[name]
        return default

    def _get_bool(self, name: str) -> bool:
        """Get a boolean configuration value from environment variables.

        Args:
            name: The name of the environment variable

        Returns:
            True if the environment variable exists and is set to 'true' or '1', False otherwise
        """
        return name in os.environ and os.environ[name].lower() in ["true", "1"]

    def get_azure_credentials(self):
        """Get Azure credentials using DefaultAzureCredential.

        Returns:
            DefaultAzureCredential instance for Azure authentication
        """
        # Cache the credentials object
        if self._azure_credentials is not None:
            return self._azure_credentials

        try:
            self._azure_credentials = DefaultAzureCredential()
            return self._azure_credentials
        except Exception as exc:
            logging.warning("Failed to create DefaultAzureCredential: %s", exc)
            return None

    def get_cosmos_database_client(self):
        """Get a Cosmos DB client for the configured database.

        Returns:
            A Cosmos DB database client
        """
        try:
            if self._cosmos_client is None:
                self._cosmos_client = CosmosClient(
                    self.COSMOSDB_ENDPOINT, credential=self.get_azure_credentials()
                )

            if self._cosmos_database is None:
                self._cosmos_database = self._cosmos_client.get_database_client(
                    self.COSMOSDB_DATABASE
                )

            return self._cosmos_database
        except Exception as exc:
            logging.error(
                "Failed to create CosmosDB client: %s. CosmosDB is required for this application.",
                exc,
            )
            raise

    def create_kernel(self):
        """Creates a new Semantic Kernel instance.

        Returns:
            A new Semantic Kernel instance
        """        # Create a new kernel instance without manually configuring OpenAI services
        # The agents will be created using Azure AI Agent Project pattern instead
        kernel = Kernel()
        return kernel

    def get_ai_project_client(self):
        """Create and return an AIProjectClient for Azure AI Foundry using from_connection_string.

        Returns:
            An AIProjectClient instance or None if running in local development mode
        """
        if self._ai_project_client is not None:
            return self._ai_project_client

        try:
            # Thought into existence by Darbot - Skip AI Project Client creation for local development
            connection_string = self.AZURE_AI_AGENT_PROJECT_CONNECTION_STRING
            
            # Check if this is a mock/local development connection string
            if connection_string and ("mock" in connection_string.lower() or "InstrumentationKey" in connection_string):
                logging.info("Detected local development mode, skipping AIProjectClient creation")
                return None
                
            credential = self.get_azure_credentials()
            if credential is None:
                raise RuntimeError(
                    "Unable to acquire Azure credentials; ensure DefaultAzureCredential is configured"
                )            # Parse connection string to extract endpoint, subscription_id, resource_group, project_name
            try:                # Connection string format: endpoint;subscription_id;resource_group;project_name
                parts = connection_string.split(';')
                if len(parts) != 4:
                    raise ValueError(f"Invalid connection string format. Expected 4 parts, got {len(parts)}")
                
                # Check if the endpoint already has a protocol
                if parts[0].startswith("http://") or parts[0].startswith("https://"):
                    endpoint = parts[0]
                else:
                    endpoint = f"https://{parts[0]}"
                
                # Strip trailing slash if present
                if endpoint.endswith("/"):
                    endpoint = endpoint[:-1]
                    
                subscription_id = parts[1]
                resource_group = parts[2]
                project_name = parts[3]
                
                # Important: For AI Foundry resources, we need to use the "services.ai.azure.com" endpoint, not cognitiveservices
                if "cognitiveservices.azure.com" in endpoint:
                    endpoint = endpoint.replace("cognitiveservices.azure.com", "services.ai.azure.com")
                    logging.info(f"Updated endpoint to AI services endpoint: {endpoint}")
                
                resource_name = self.AZURE_AI_RESOURCE_NAME
                if not resource_name:
                    # Parse from the endpoint
                    resource_name = endpoint.split('//')[1].split('.')[0]
                    logging.info(f"Extracted resource name from endpoint: {resource_name}")
                
                logging.info(f"Creating AIProjectClient with endpoint={endpoint}, subscription_id={subscription_id}, resource_group={resource_group}, resource_name={resource_name}, project_name={project_name}")
                
                try:
                    # Try with the services.ai.azure.com endpoint first
                    self._ai_project_client = AIProjectClient(
                        endpoint=endpoint,
                        subscription_id=subscription_id,
                        resource_group_name=resource_group,
                        project_name=project_name,
                        credential=credential
                    )
                except Exception as e:
                    if "MachineLearningServices" in str(e):
                        logging.warning(f"Received Machine Learning Services error. This might be because we're using a Cognitive Services resource. Error: {e}")
                        # Special handling for Cognitive Services AI Projects
                        # For Cognitive Services AI projects, we need to use a different format
                        # We need to initialize the AIProjectClient with the correct AI project path for CognitiveServices
                        logging.info("Trying with Cognitive Services AI project path")
                        self._ai_project_client = AIProjectClient(
                            endpoint=endpoint,
                            subscription_id=subscription_id,
                            resource_group_name=resource_group, 
                            project_name=project_name,
                            credential=credential,
                            resource_name=resource_name,  # Add resource name for Cognitive Services
                        )
                    else:
                        # Re-raise the original error if it's not related to resource type
                        raise
            except Exception as parse_exc:
                logging.error(f"Failed to parse connection string: {parse_exc}")
                raise

            return self._ai_project_client
        except Exception as exc:
            logging.error("Failed to create AIProjectClient: %s", exc)
            logging.info("Continuing without AIProjectClient for local development")
            return None


# Create a global instance of AppConfig
config = AppConfig()

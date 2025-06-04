# dependency_health_checks.py
"""
Enhanced health checks for application dependencies
Thought into existence by Darbot
"""
import asyncio
import logging
import os
from typing import Optional

from azure.core.exceptions import AzureError
from azure.cosmos.exceptions import CosmosHttpResponseError

from app_config import AppConfig
from middleware.health_check import HealthCheckResult


class DependencyHealthChecks:
    """Health checks for application dependencies"""

    def __init__(self, config: AppConfig):
        self.config = config

    async def check_cosmos_db(self) -> HealthCheckResult:
        """Check CosmosDB connectivity"""
        try:
            if not self.config.COSMOSDB_ENDPOINT:
                return HealthCheckResult(
                    False, "CosmosDB endpoint not configured (using local memory)"
                )

            # Get credentials and test connection
            cosmos_client = self.config.get_cosmos_client()
            if not cosmos_client:
                return HealthCheckResult(
                    False, "Failed to create CosmosDB client"
                )

            # Try a simple read operation with timeout
            try:
                database_client = cosmos_client.get_database_client(
                    self.config.COSMOSDB_DATABASE or "default"
                )
                
                # Test connection with timeout
                await asyncio.wait_for(
                    database_client.read(),
                    timeout=5.0
                )
                
                return HealthCheckResult(True, "CosmosDB connection successful")

            except asyncio.TimeoutError:
                return HealthCheckResult(
                    False, "CosmosDB connection timeout (>5s)"
                )
            except CosmosHttpResponseError as e:
                if e.status_code == 404:
                    return HealthCheckResult(
                        False, f"CosmosDB database '{self.config.COSMOSDB_DATABASE}' not found"
                    )
                return HealthCheckResult(
                    False, f"CosmosDB error: {e.message}"
                )

        except AzureError as e:
            return HealthCheckResult(
                False, f"Azure authentication error: {str(e)}"
            )
        except Exception as e:
            logging.exception("Unexpected error in CosmosDB health check")
            return HealthCheckResult(
                False, f"CosmosDB health check failed: {str(e)}"
            )

    async def check_azure_openai(self) -> HealthCheckResult:
        """Check Azure OpenAI connectivity"""
        try:
            if not self.config.AZURE_OPENAI_ENDPOINT:
                return HealthCheckResult(
                    False, "Azure OpenAI endpoint not configured"
                )

            # Basic configuration check
            if not self.config.AZURE_OPENAI_DEPLOYMENT_NAME:
                return HealthCheckResult(
                    False, "Azure OpenAI deployment name not configured"
                )

            # For now, just check configuration presence
            # A full connectivity test would require making an actual API call
            return HealthCheckResult(
                True, f"Azure OpenAI configured: {self.config.AZURE_OPENAI_DEPLOYMENT_NAME}"
            )

        except Exception as e:
            logging.exception("Unexpected error in Azure OpenAI health check")
            return HealthCheckResult(
                False, f"Azure OpenAI health check failed: {str(e)}"
            )

    async def check_azure_ai_projects(self) -> HealthCheckResult:
        """Check Azure AI Projects connectivity"""
        try:
            if not self.config.AZURE_AI_AGENT_PROJECT_CONNECTION_STRING:
                return HealthCheckResult(
                    False, "Azure AI Projects connection string not configured"
                )

            # Get the AI project client
            ai_client = self.config.get_ai_project_client()
            if not ai_client:
                return HealthCheckResult(
                    False, "Failed to create Azure AI Projects client"
                )

            # For now, just verify client creation
            # A full test would require making an actual API call
            return HealthCheckResult(
                True, "Azure AI Projects client created successfully"
            )

        except AzureError as e:
            return HealthCheckResult(
                False, f"Azure AI Projects authentication error: {str(e)}"
            )
        except Exception as e:
            logging.exception("Unexpected error in Azure AI Projects health check")
            return HealthCheckResult(
                False, f"Azure AI Projects health check failed: {str(e)}"
            )

    async def check_environment_variables(self) -> HealthCheckResult:
        """Check critical environment variables"""
        try:
            missing_vars = []
            critical_vars = [
                "AZURE_AI_SUBSCRIPTION_ID",
                "AZURE_AI_RESOURCE_GROUP", 
                "AZURE_AI_PROJECT_NAME",
                "AZURE_AI_AGENT_PROJECT_CONNECTION_STRING",
                "AZURE_OPENAI_ENDPOINT",
                "AZURE_OPENAI_DEPLOYMENT_NAME"
            ]

            for var in critical_vars:
                if not os.getenv(var):
                    missing_vars.append(var)

            if missing_vars:
                return HealthCheckResult(
                    False, f"Missing critical environment variables: {', '.join(missing_vars)}"
                )

            return HealthCheckResult(
                True, f"All {len(critical_vars)} critical environment variables configured"
            )

        except Exception as e:
            logging.exception("Unexpected error in environment variables health check")
            return HealthCheckResult(
                False, f"Environment variables health check failed: {str(e)}"
            )

    async def check_semantic_kernel(self) -> HealthCheckResult:
        """Check Semantic Kernel functionality"""
        try:
            # Try to import and create a basic kernel
            from semantic_kernel.kernel import Kernel
            
            kernel = Kernel()
            if kernel:
                return HealthCheckResult(
                    True, "Semantic Kernel initialized successfully"
                )
            else:
                return HealthCheckResult(
                    False, "Failed to initialize Semantic Kernel"
                )

        except ImportError as e:
            return HealthCheckResult(
                False, f"Semantic Kernel import error: {str(e)}"
            )
        except Exception as e:
            logging.exception("Unexpected error in Semantic Kernel health check")
            return HealthCheckResult(
                False, f"Semantic Kernel health check failed: {str(e)}"
            )


async def create_health_checks(config: AppConfig) -> dict:
    """Create a dictionary of health check functions"""
    health_checker = DependencyHealthChecks(config)
    
    return {
        "cosmos_db": health_checker.check_cosmos_db,
        "azure_openai": health_checker.check_azure_openai,
        "azure_ai_projects": health_checker.check_azure_ai_projects,
        "environment_variables": health_checker.check_environment_variables,
        "semantic_kernel": health_checker.check_semantic_kernel,
    }
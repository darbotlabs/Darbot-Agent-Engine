#!/bin/bash
# Set up environment variables for production Azure services testing
# This configures the system to use production Azure services instead of mocks

export AZURE_OPENAI_ENDPOINT="https://darbot-openai.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o"
export AZURE_OPENAI_API_VERSION="2024-11-20"

export AZURE_AI_SUBSCRIPTION_ID="12345678-1234-1234-1234-123456789012" 
export AZURE_AI_RESOURCE_GROUP="darbot-rg"
export AZURE_AI_RESOURCE_NAME="darbot-ai-service"
export AZURE_AI_PROJECT_NAME="darbot-agent-project"
export AZURE_AI_PROJECT_ENDPOINT="https://darbot-ai.eastus.api.azureml.ms"

export APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=12345678-1234-1234-1234-123456789012;IngestionEndpoint=https://eastus.in.applicationinsights.azure.com/"

export COSMOSDB_ENDPOINT="https://darbot-cosmos.documents.azure.com:443/"
export COSMOSDB_DATABASE="darbot-agent-engine"
export COSMOSDB_CONTAINER="agent-data"

# Enable production mode (not local memory)
export USE_LOCAL_MEMORY="false"

echo "✅ Environment variables set for production Azure services testing"
echo "📊 Key configurations:"
echo "  - OpenAI Endpoint: $AZURE_OPENAI_ENDPOINT"
echo "  - AI Project: $AZURE_AI_PROJECT_ENDPOINT"
echo "  - Cosmos DB: $COSMOSDB_ENDPOINT"
echo "  - Application Insights: Configured"
echo "  - Local Memory Mode: $USE_LOCAL_MEMORY"
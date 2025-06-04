# Thought into existence by Darbot
import os
from azure.cosmos import CosmosClient, exceptions
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_cosmos_connection():
    """Check connection to Azure Cosmos DB using keyless authentication."""
    
    print("Checking Cosmos DB connection with keyless authentication...")
    
    # Get connection details from environment variables
    cosmos_endpoint = os.environ.get("COSMOSDB_ENDPOINT")
    cosmos_database = os.environ.get("COSMOSDB_DATABASE", "darbot-dev")
    cosmos_container = os.environ.get("COSMOSDB_CONTAINER", "agent-conversations")
    
    if not cosmos_endpoint:
        print("❌ Missing COSMOSDB_ENDPOINT in environment variables")
        return False
    
    print(f"Using keyless authentication for Cosmos DB access: {cosmos_endpoint}")
    
    # Use DefaultAzureCredential for keyless authentication
    credential = DefaultAzureCredential()
    client = CosmosClient(cosmos_endpoint, credential)
    database_name = cosmos_database
    container_name = cosmos_container

    try:
        # Check database access
        print(f"Checking database: {database_name}")
        database = client.get_database_client(database_name)
        
        # Check if database exists
        try:
            database_properties = database.read()
            print(f"✅ Successfully connected to database: {database_properties['id']}")
        except exceptions.CosmosResourceNotFoundError:
            print(f"❌ Database '{database_name}' does not exist!")
            return False
            
        # Check container access
        print(f"Checking container: {container_name}")
        container = database.get_container_client(container_name)
        
        # Check if container exists
        try:
            container_properties = container.read()
            print(f"✅ Successfully connected to container: {container_properties['id']}")
            
            # Get item count
            query = "SELECT VALUE COUNT(1) FROM c"
            items_count = list(container.query_items(query, enable_cross_partition_query=True))[0]
            print(f"📊 Container contains {items_count} items")
            
            # Query for structure example if any items exist
            if items_count > 0:
                query = "SELECT TOP 1 * FROM c"
                items = list(container.query_items(query, enable_cross_partition_query=True))
                print("📋 Sample item structure:", items[0])
                
                # Check if there are any task items
                query = "SELECT * FROM c WHERE c.type = 'task' OR c.category = 'task' OR c.itemType = 'task'"
                tasks = list(container.query_items(query, enable_cross_partition_query=True))
                print(f"🔍 Found {len(tasks)} items that could be tasks")
                
        except exceptions.CosmosResourceNotFoundError:
            print(f"❌ Container '{container_name}' does not exist!")
            return False
            
        return True
        
    except exceptions.CosmosHttpResponseError as e:
        print(f"❌ Error connecting to Cosmos DB: {str(e)}")
        return False

if __name__ == "__main__":
    check_cosmos_connection()

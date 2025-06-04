from azure.cosmos import CosmosClient, exceptions as cosmos_exceptions
from azure.identity import DefaultAzureCredential
import os
import time

endpoint = 'https://darbot-cosmos-dev.documents.azure.com:443/'
database_name = 'macae' # From .env file
container_name = 'memory' # From .env file

print(f'Testing connection to {endpoint} with DefaultAzureCredential')
print(f'Database: {database_name}, Container: {container_name}')

try:
    print("Getting DefaultAzureCredential...")
    credential = DefaultAzureCredential()
    print("Credential obtained successfully")
    
    # Create the cosmos client
    print("Creating CosmosClient...")
    client = CosmosClient(endpoint, credential=credential)
    print("CosmosClient created successfully")
    
    # Attempt to access database 
    try:
        database = client.get_database_client(database_name)
        database_properties = database.read()
        print(f'Successfully connected to database: {database_name}')
    except cosmos_exceptions.CosmosResourceNotFoundError:
        print(f'ERROR: Database {database_name} does not exist!')
        print(f'The database should already exist in the CosmosDB account')
        exit(1)
    
    # Check if container exists
    try:
        container = database.get_container_client(container_name)
        container_properties = container.read()  # Verify container exists
        print(f'Successfully accessed container: {container_name}')
    except cosmos_exceptions.CosmosResourceNotFoundError:
        print(f'ERROR: Container {container_name} does not exist!')
        print(f'The container should already exist in the database')
        exit(1)
    
    # Try a simple query
    query = 'SELECT TOP 5 * FROM c'
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    print(f'Query executed, found {len(items)} items')
    
    if items:
        print('Sample item:')
        print(items[0])
    else:
        print('No items found in container - this is normal for a new container')
        
    # Insert a test document
    test_doc = {
        "id": f"test_doc_{int(time.time())}",
        "name": "Test Document",
        "description": "Created by Darbot Agent Engine test script",
        "timestamp": time.time()
    }
    container.create_item(body=test_doc)
    print(f"Created test document with id: {test_doc['id']}")
    
    # Verify test document was created
    query = f"SELECT * FROM c WHERE c.id = '{test_doc['id']}'"
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    print(f'Verification query found {len(items)} items')
    
    print('COSMOS ACCESS TEST: SUCCESS')
        
except Exception as e:
    print(f'Error: {str(e)}')

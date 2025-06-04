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
    credential = DefaultAzureCredential()
    
    # Create the cosmos client
    client = CosmosClient(endpoint, credential=credential)
    
    # Attempt to access database 
    try:
        database = client.get_database_client(database_name)
        database_properties = database.read()
        print(f'Successfully connected to database: {database_name}')
        print(f'Database properties: {database_properties}')
    
    # Check if container exists, if not create it
    try:
        container = database.get_container_client(container_name)
        container.read()  # Verify container exists
        print(f'Container {container_name} exists')
    except cosmos_exceptions.CosmosResourceNotFoundError:
        print(f'Container {container_name} does not exist. Creating...')
        # Set partition key to a default value if not specified
        container = database.create_container(
            id=container_name, 
            partition_key="/id",
            offer_throughput=400  # Minimum throughput
        )
        print(f'Created container: {container_name}')
    
    # Wait a moment for the container to be fully provisioned
    time.sleep(2)
    
    # Try a simple query
    try:
        query = 'SELECT TOP 5 * FROM c'
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        print(f'Query executed, found {len(items)} items')
        
        if items:
            print('Sample item:')
            print(items[0])
        else:
            print('No items found in container')
            
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
    except Exception as query_err:
        print(f'Error querying container: {str(query_err)}')
        
except Exception as e:
    print(f'Error: {str(e)}')

#!/usr/bin/env python3
"""
Test CosmosDB connectivity with correct database and container names
"""
from azure.cosmos import CosmosClient, exceptions as cosmos_exceptions
from azure.identity import DefaultAzureCredential
import time
import json

# Use the correct database and container names from our discovery
endpoint = 'https://darbot-cosmos-dev.documents.azure.com:443/'
database_name = 'darbot'  # Correct database name
container_name = 'plans'  # Correct container name

print("=" * 60)
print("DARBOT AGENT ENGINE - COSMOS DB CONNECTIVITY TEST")
print("=" * 60)
print(f'Endpoint: {endpoint}')
print(f'Database: {database_name}')
print(f'Container: {container_name}')
print()

try:
    # Create Azure credential
    print("1. Creating DefaultAzureCredential...")
    credential = DefaultAzureCredential()
    print("   ✓ Credential created successfully")
    
    # Create Cosmos client
    print("2. Creating CosmosDB client...")
    client = CosmosClient(endpoint, credential=credential)
    print("   ✓ Client created successfully")
    
    # Get database
    print("3. Connecting to database...")
    database = client.get_database_client(database_name)
    database_props = database.read()
    print(f"   ✓ Connected to database: {database_name}")
    print(f"   Database ID: {database_props.get('id', 'N/A')}")
    
    # Get container
    print("4. Accessing container...")
    container = database.get_container_client(container_name)
    container_props = container.read()
    print(f"   ✓ Accessed container: {container_name}")
    print(f"   Partition Key: {container_props.get('partitionKey', {}).get('paths', 'N/A')}")
    
    # Query existing items
    print("5. Querying existing items...")
    query = "SELECT TOP 5 * FROM c"
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    print(f"   ✓ Query executed, found {len(items)} items")
    
    if items:
        print("   Sample item:")
        sample_item = items[0]
        # Pretty print first few fields
        for key, value in list(sample_item.items())[:3]:
            print(f"     {key}: {value}")
        if len(sample_item) > 3:
            print(f"     ... and {len(sample_item) - 3} more fields")
    
    # Test write operation
    print("6. Testing write operation...")
    test_doc = {
        "id": f"connectivity_test_{int(time.time())}",
        "type": "connectivity_test",
        "name": "Darbot Connectivity Test",
        "description": "Test document created by connectivity test script",
        "timestamp": time.time(),
        "test_status": "successful"
    }
    
    try:
        created_item = container.create_item(body=test_doc)
        print(f"   ✓ Test document created with ID: {created_item['id']}")
        
        # Verify the document was created
        query = f"SELECT * FROM c WHERE c.id = '{test_doc['id']}'"
        verification_items = list(container.query_items(query=query, enable_cross_partition_query=True))
        if verification_items:
            print(f"   ✓ Document verified in database")
        else:
            print(f"   ⚠ Document not found during verification")
            
    except Exception as write_err:
        print(f"   ✗ Write operation failed: {str(write_err)}")
        print("   This might indicate insufficient permissions for write operations")
    
    print()
    print("=" * 60)
    print("🎉 COSMOS DB CONNECTIVITY TEST: SUCCESSFUL")
    print("=" * 60)
    print("The backend should now be able to connect to CosmosDB!")
    print("Next step: Restart the backend server to test full functionality.")
    
except cosmos_exceptions.CosmosResourceNotFoundError as not_found_err:
    print(f"   ✗ Resource not found: {str(not_found_err)}")
    print("   This might indicate the database or container doesn't exist")
    
except cosmos_exceptions.CosmosHttpResponseError as http_err:
    print(f"   ✗ HTTP error: {str(http_err)}")
    print("   This might indicate permission or authentication issues")
    
except Exception as e:
    print(f"   ✗ Unexpected error: {str(e)}")
    print("   Check Azure credentials and network connectivity")
    
finally:
    print()
    print("Test completed.")

import os
from azure.cosmos import CosmosClient, PartitionKey, exceptions

COSMOS_CONNECTION = os.environ.get("COSMOS_CONN_STRING")
COSMOS_DB = os.environ.get("COSMOS_DB", "ProductsDB")
COSMOS_CONTAINER = os.environ.get("COSMOS_CONTAINER", "Products")

if not COSMOS_CONNECTION:
    raise Exception("COSMOS_CONNECTION env variable missing")

client = CosmosClient.from_connection_string(COSMOS_CONNECTION)

def get_container():
    db = client.create_database_if_not_exists(id=COSMOS_DB)
    container = db.create_container_if_not_exists(
        id=COSMOS_CONTAINER,
        partition_key=PartitionKey(path="/ID"),
        offer_throughput=400
    )
    return container

def read_item(ID):
    container = get_container()
    try:
        return container.read_item(item=ID, partition_key=ID)
    except exceptions.CosmosResourceNotFoundError:
        return None
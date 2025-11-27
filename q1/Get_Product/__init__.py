import azure.functions as func
import json
from cosmos_client import get_container

def main(req: func.HttpRequest, ID: str) -> func.HttpResponse:
    container = get_container()
    try:
        item = container.read_item(item=ID, partition_key=ID)
        return func.HttpResponse(json.dumps(item), mimetype="application/json", status_code=200)
    except Exception as e:
        return func.HttpResponse("Product not found", status_code=404)

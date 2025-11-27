import azure.functions as func
import json
from cosmos_client import get_container

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
    except:
        return func.HttpResponse("Invalid JSON", status_code=400)

    if not body or "id" not in body:
        return func.HttpResponse("Missing 'id' in body", status_code=400)

    container = get_container()
    created = container.create_item(body)

    return func.HttpResponse(
        json.dumps(created),
        mimetype="application/json",
        status_code=201
    )
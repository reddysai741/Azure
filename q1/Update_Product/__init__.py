import azure.functions as func
import json
from cosmos_client import get_container

def main(req: func.HttpRequest) -> func.HttpResponse:
    id = req.route_params.get("id")

    if not id:
        return func.HttpResponse("ID missing", status_code=400)

    try:
        body = req.get_json()
    except:
        return func.HttpResponse("Invalid JSON", status_code=400)

    container = get_container()

    try:
        item = container.read_item(item=id, partition_key=id)
    except:
        return func.HttpResponse("Item not found", status_code=404)

    for key, value in body.items():
        item[key] = value

    updated = container.replace_item(item=id, body=item)

    return func.HttpResponse(
        json.dumps(updated),
        mimetype="application/json",
        status_code=200
    )

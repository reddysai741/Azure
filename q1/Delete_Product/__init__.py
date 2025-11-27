import azure.functions as func
from cosmos_client import get_container

def main(req: func.HttpRequest) -> func.HttpResponse:
    id = req.route_params.get("ID")

    if not id:
        return func.HttpResponse("ID missing", status_code=400)

    container = get_container()

    try:
        container.delete_item(item=id, partition_key=id)
    except:
        return func.HttpResponse("Item not found", status_code=404)

    return func.HttpResponse("Deleted Successfully", status_code=200)

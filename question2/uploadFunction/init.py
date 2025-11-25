import azure.functions as func
from azure.storage.blob import BlobServiceClient
import os
import json

def main(req: func.HttpRequest, msg: func.Out[str]) -> func.HttpResponse:
    try:

        file = req.files.get('file')
        if not file:
            return func.HttpResponse("No file uploaded.", status_code=400)

        blob_service = BlobServiceClient.from_connection_string(
            os.environ["AzureWebJobsStorage"]
        )

        uploads_container = blob_service.get_container_client("uploads")

        blob_client = uploads_container.get_blob_client(file.filename)
        blob_client.upload_blob(file.stream, overwrite=True)

        blob_url = blob_client.url

        job = {
            "blobUrl": blob_url,
            "sizes": [320, 1024]
        }
        msg.set(json.dumps(job))

        return func.HttpResponse(
            f"Uploaded and queued successfully: {blob_url}", status_code=200
        )

    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)
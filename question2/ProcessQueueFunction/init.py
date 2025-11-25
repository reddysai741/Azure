import azure.functions as func
from azure.storage.blob import BlobServiceClient
from urllib.parse import unquote
from PIL import Image
import io
import json
import uuid
import datetime
import os
import time

def main(msg: func.QueueMessage):
    start_time = time.time()

    conn_str = os.getenv("AZURE_STORAGE_CONNECTION")

    blob_service = BlobServiceClient.from_connection_string(conn_str)

    message = msg.get_json()
    blob_url = message["blobUrl"]
    sizes = message["sizes"]

    try:
        
        filename = unquote(blob_url.split("/")[-1])

    
        original_blob = blob_service.get_blob_client(
            container="uploads",
            blob=filename
        )

        image_bytes = original_blob.download_blob().readall()
        image = Image.open(io.BytesIO(image_bytes))

        resized_urls = []

        for size in sizes:
            img_copy = image.copy()
            img_copy.thumbnail((size, size))

            buffer = io.BytesIO()
            img_copy.save(buffer, format="JPEG")
            buffer.seek(0)

            resized_blob = blob_service.get_blob_client(
                container="resized",
                blob=f"{size}/{uuid.uuid4()}.jpg"
            )

            resized_blob.upload_blob(buffer, overwrite=True)
            resized_urls.append(resized_blob.url)

        log_data = {
            "original": blob_url,
            "resized": resized_urls,
            "processing_time": time.time() - start_time,
            "status": "success"
        }

        log_blob = blob_service.get_blob_client(
            container="function-logs",
            blob=f"ImageResizer/{datetime.date.today()}/{uuid.uuid4()}.json"
        )

        log_blob.upload_blob(json.dumps(log_data), overwrite=True)

    except Exception as e:
        if msg.dequeue_count >= 5:
            error_log = {
                "original": blob_url,
                "error": str(e),
                "status": "failed after retries"
            }

            log_blob = blob_service.get_blob_client(
                container="function-logs",
                blob=f"ImageResizer/{datetime.date.today()}/{uuid.uuid4()}.json"
            )

            log_blob.upload_blob(json.dumps(error_log), overwrite=True)
            return

        raise e
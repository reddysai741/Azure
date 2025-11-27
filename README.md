# 1. Simple HTTP CRUD API (Azure Functions + Cosmos DB) — Beginner [GitHub Repo](https://github.com/reddysai741/Azure/tree/main/q1)


 Problem statement -

 
Create a small Products CRUD API using Python Azure Functions that stores product documents 
in Azure Cosmos DB (SQL API). Deploy locally and to Azure.

 Requirements / Acceptance
 
 • Endpoints:
 ◦ POST /api/products — create product (body includes id, name, price)
 
 ◦ GET /api/products — list products
 
 ◦ GET /api/products/{id} — retrieve product
 
 ◦ PUT /api/products/{id} — update product
 
 ◦ DELETE /api/products/{id} — delete product

 ### Architecture of task

                 ┌──────────────────────────┐
                │   Azure Function App     │
                │ (HTTP Triggered APIs)    │
                │--------------------------│
                │  create-product          │
                │  list-products           │
                │  get-product             │
                │  update-product          │
                │  delete-product          │
                └──────────┬──────────────┘
                           │
                           ▼
         ┌─────────────────────────────────────┐
         │   Cosmos DB Client (Shared Module)  │
         │  (uses account URL + key)           │
         └──────────┬──────────────────────────┘
                    │
                    ▼
         ┌─────────────────────────────────────┐
         │      Azure Cosmos DB (SQL API)      │
         │-------------------------------------│
         │  Account: <Cosmos Account Name>      │
         │  Database: ProductsDB                │
         │  Container: Products                 │
         │  Partition Key: /id                  │
         └─────────────────────────────────────┘
<img width="1350" height="172" alt="Screenshot 2025-11-25 112927" src="https://github.com/user-attachments/assets/6e044a44-7dda-4e2c-8bfd-54f00f9c391c" />


# 2. Queue-driven Image Resizer (Functions + Storage Queue + Blob Storage) — Intermediate

 Problem statement- [GitHub Repo](https://github.com/reddysai741/Azure/tree/main/question2)

 
Build a system where an HTTP API accepts an image upload request, stores the uploaded image to 
Blob Storage, and enqueues a job to image-jobs queue. A Queue-triggered Function picks up 
the job, resizes the image into two sizes, stores resized images into a different container, and logs 
results in blob storage (JSON).

 Requirements / Acceptance
 
 • POST /api/upload (HTTP Function) accepts multipart or base64; stores original to 
uploads/.
 
 • Enqueue message JSON { "blobUrl": "...", "sizes":[320, 1024] }.
 
 • Queue job function resizes image to each size, stores under container resized/<size>/....
 
 • After processing, write a JSON log blob under function-logs/ImageResizer/
 <date>/...json with original URL, output URLs, processing time, status.

 ## Architecture of task

 <img width="2816" height="1536" alt="Gemini_Generated_Image_7o4f5e7o4f5e7o4f" src="https://github.com/user-attachments/assets/871ff23f-d559-405d-a226-28a471314396" />

                          
<img width="1356" height="407" alt="Screenshot 2025-11-25 172316" src="https://github.com/user-attachments/assets/29e7a9ae-135d-43ed-b7ff-2377303ef963" />



# 3. Event Grid: Auto-index Blob Metadata into Cosmos (Event Grid + Functions + Cosmos) — Intermediate [GitHub Repo](https://github.com/reddysai741/Azure/tree/main/q3)


Problem statement 
Whenever a blob is created in documents container, Event Grid triggers a Function that reads 
blob metadata and content, extracts a title and word-count, and indexes a document record into 
Cosmos DB.


 Requirements / Acceptance
 • Use Event Grid trigger (Function) bound to the Storage account blob-created events.
 
 • For each new blob, extract:
 
 ◦ blobName, container, url, size, contentType
 
 ◦ title: first H1 (or first line) if text file
 
 ◦ wordCount: number of words (for text)
 
 • Insert a document into Cosmos DB Documents container with id=blobName.
 
 • Avoid duplicate inserts (id uniqueness).
 
 • Provide a function log and sample query for Cosmos to get largest documents.
 
 Sample Cosmos document
 {
 }
  "id": "file1.txt",
  
  "url": "https://.../documents/file1.txt",
  
  "size": 1234,
  
  "title": "My Notes",
  
  "wordCount": 345,
  
  "uploadedOn": "2025-11-24T..."

## Architecture of task

<img width="2816" height="1536" alt="Gemini_Generated_Image_q92hmqq92hmqq92h" src="https://github.com/user-attachments/assets/d01d19ad-361a-4beb-a30a-28de00dca8bf" />
 
  
  
<img width="897" height="242" alt="Screenshot 2025-11-26 142934" src="https://github.com/user-attachments/assets/b09d01b1-f8c1-4e4f-9469-886990158b6d" />
<img width="1349" height="547" alt="Screenshot 2025-11-27 072418" src="https://github.com/user-attachments/assets/85f869cc-6042-44c2-a5d7-5f57f8c68f21" />
<img width="1283" height="488" alt="Screenshot 2025-11-27 074034" src="https://github.com/user-attachments/assets/be605837-2b07-40cb-939a-fb63d6295852" />
<img width="1052" height="593" alt="Screenshot 2025-11-27 102008" src="https://github.com/user-attachments/assets/9827b47c-cc49-4af7-aed8-35b64373c1d4" />
<img width="1282" height="473" alt="Screenshot 2025-11-27 102054" src="https://github.com/user-attachments/assets/92e14ef6-7fad-43bf-aa03-8548314e028e" />
<img width="1309" height="470" alt="Screenshot 2025-11-27 102142" src="https://github.com/user-attachments/assets/9d782b53-b24c-4872-93e7-92de89a59c6f" />
<img width="1271" height="530" alt="Screenshot 2025-11-27 102356" src="https://github.com/user-attachments/assets/fd9af985-3828-4f59-9242-8e87b549db64" />


# 6. Scheduled Cleanup Job (Timer Trigger + Azure SQL + Storage) — Beginner/Intermediate [GitHub Repo](https://github.com/reddysai741/Azure/tree/main/q6)

Problem statement 

Create a Timer-triggered Function that runs nightly and archives old records older than 30 days 
from Azure SQL into Blob Storage as newline-delimited JSON. Delete records once archived.

 Requirements / Acceptance
 
 • Timer Trigger runs daily at 02:00 UTC.
 
 • Query Orders table in Azure SQL for rows older than 30 days.
 
 • Write a blob file archive/orders/YYYY/MM/DD/orders
<timestamp>.ndjson with one JSON object per line.
 
 • After successful write, delete those rows from the SQL table (transactional if many).
 
 • Log number of archived rows and archive blob URL in Application Insights or blob logger.


                  ┌────────────────────────────────────┐
                 │   Timer Trigger (02:00 UTC Daily)  │
                 └───────────────┬────────────────────┘
                                 │
                                 ▼
               ┌────────────────────────────────────┐
               │ Calculate cutoff = now - 30 days   │
               └─────────────────┬──────────────────┘
                                 │
                                 ▼
               ┌────────────────────────────────────┐
               │ Query Azure SQL Orders in batches  │
               │ (1000 rows per batch)             │
               └─────────────────┬──────────────────┘
                                 │
                                 ▼
       ┌────────────────────────────────────────────────────────┐
       │  Stream record → NDJSON Blob (append line by line)     │
       │  ALSO write ID to temp file for deletion               │
       └────────────────────┬────────────────────────────────────┘
                             │
                             ▼
          ┌───────────────────────────────────────────┐
          │ Finish Blob Upload → archive/orders/...   │
          └────────────────────┬──────────────────────┘
                               │
                               ▼
       ┌────────────────────────────────────────────────────────┐
       │  Read IDs from temp file in batches                   │
       │  SQL DELETE IN BATCHES inside TRANSACTION             │
       └────────────────────┬────────────────────────────────────┘
                             │
                             ▼
             ┌──────────────────────────────────┐
             │  Log details (counts + blob URL) │
             │  Clean temp files                │
             └──────────────────────────────────┘

<img width="1194" height="513" alt="Screenshot 2025-11-26 163348" src="https://github.com/user-attachments/assets/cc5abee6-0298-425f-97ef-8e184f7982a3" />



## 1. Simple HTTP CRUD API (Azure Functions + Cosmos DB) — Beginner [GitHub Repo](https://github.com/reddysai741/Azure/tree/main)


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


## 2. Queue-driven Image Resizer (Functions + Storage Queue + Blob Storage) — Intermediate

 Problem statement- [GitHub Repo](https://github.com/reddysai741/Azure/tree/main)

 
Build a system where an HTTP API accepts an image upload request, stores the uploaded image to 
Blob Storage, and enqueues a job to image-jobs queue. A Queue-triggered Function picks up 
the job, resizes the image into two sizes, stores resized images into a different container, and logs 
results in blob storage (JSON).
 Requirements / Acceptance
 • POST /api/upload (HTTP Function) accepts multipart or base64; stores original to 
uploads/.
 • Enqueue message JSON { "blobUrl": "...", "sizes":[320, 1024] }.
 • Queue job function resizes image to each size, stores under container resized/
 <size>/....
 • After processing, write a JSON log blob under function-logs/ImageResizer/
 <date>/...json with original URL, output URLs, processing time, status


                             ┌───────────────┐
                            │     Client     │
                            └───────┬───────┘
                                    │
                          POST /api/upload
                                    │
                       ┌────────────▼────────────┐
                       │ HTTP Upload Function     │
                       │  - validate input         │
                       │  - save to uploads/       │
                       │  - enqueue resize job     │
                       └───────┬──────────┬───────┘
                               │          │
                Writes Blob    │          │  Enqueue JSON
                      ┌────────▼──┐   ┌───▼────────────┐
                      │ uploads/  │   │ image-jobs Queue│
                      └───────────┘   └───────┬────────┘
                                              │
                                      Auto-trigger by message
                                              │
                                    ┌─────────▼──────────┐
                                    │ Queue-triggered     │
                                    │ Image Resizer Func  │
                                    │  - download image    │
                                    │  - resize sizes      │
                                    │  - save outputs      │
                                    │  - write logs        │
                                    └───────┬──────────────┘
                       Writes resized blobs │
                                           │
                        ┌──────────────────▼───────────┐
                        │ resized/<size>/               │
                        └──────────────────────────────┘

                        Writes log JSON
                        ┌───────────────────────────────┐
                        │ function-logs/ImageResizer/   │
                        └───────────────────────────────┘
<img width="1356" height="407" alt="Screenshot 2025-11-25 172316" src="https://github.com/user-attachments/assets/29e7a9ae-135d-43ed-b7ff-2377303ef963" />


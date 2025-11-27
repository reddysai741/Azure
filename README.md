## 1. Simple HTTP CRUD API (Azure Functions + Cosmos DB) — Beginner
 Problem statement 
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



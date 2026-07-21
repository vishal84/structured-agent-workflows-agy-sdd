# Design Specification: BigQuery Integration for E-Commerce Dashboard

* Date: 2026-07-21
* Status: Approved
* Author: Antigravity AI

## 1. Goal
Upgrade the FastAPI dashboard backend to run live queries against the `thelook_ecommerce` dataset in BigQuery instead of reading from local CSV files. The FastAPI endpoints and JSON schemas returned to the frontend must remain unchanged.

## 2. Requirements & Constraints
* **Client Library**: Use the official `google-cloud-bigquery` library.
* **Aggregations**: Perform data merging and grouping directly in BigQuery using SQL queries, avoiding downloading large datasets into local memory.
* **Configuration**: Read the project ID and dataset ID from environment variables:
  * `BIGQUERY_PROJECT_ID` (default: `agents-cli-503022`)
  * `BIGQUERY_DATASET_ID` (default: `thelook_ecommerce`)
* **Credentials**: Use Application Default Credentials (ADC).
* **Caching**: None required. Queries run directly on every request.

## 3. Architecture
```
┌──────────────────────────────────────┐
│        Web UI (HTML / JS)            │
└──────────────────┬───────────────────┘
                   │ FastAPI endpoints
┌──────────────────▼───────────────────┐
│     FastAPI App (src/main.py)        │
└──────────────────┬───────────────────┘
                   │ Call functions
┌──────────────────▼───────────────────┐
│   Data Service (src/data_service.py) │
└──────────────────┬───────────────────┘
                   │ BQ Client & SQL
┌──────────────────▼───────────────────┐
│          Google BigQuery             │
└──────────────────────────────────────┘
```

## 4. Proposed Changes

### A. Dependencies (`pyproject.toml`)
Add `google-cloud-bigquery` dependency.

### B. Data Service (`src/data_service.py`)
1. Import `google.cloud.bigquery`.
2. Construct client using environment variables.
3. Update functions:
   * [get_revenue_trend](file:///home/vishal/sdd-agy-bigquery-dashboard/src/data_service.py#L7)
   * [get_top_products](file:///home/vishal/sdd-agy-bigquery-dashboard/src/data_service.py#L29)
   * [get_order_status_breakdown](file:///home/vishal/sdd-agy-bigquery-dashboard/src/data_service.py#L52)
   * [get_category_performance](file:///home/vishal/sdd-agy-bigquery-dashboard/src/data_service.py#L63)
   * [get_dashboard_summary](file:///home/vishal/sdd-agy-bigquery-dashboard/src/data_service.py#L86)

### C. SQL Query Specifications

#### 1. Revenue Trend
Runs queries to fetch daily completed order sales.
```sql
SELECT DATE(o.created_at) AS date, ROUND(SUM(oi.sale_price), 2) AS revenue
FROM `{project_id}.{dataset_id}.orders` o
JOIN `{project_id}.{dataset_id}.order_items` oi ON o.order_id = oi.order_id
WHERE o.status = 'Complete'
GROUP BY date
ORDER BY date
```

#### 2. Top Products
Retrieves names and sales counts for top-selling products. Uses query parameter for limit.
```sql
SELECT p.name, ROUND(SUM(oi.sale_price), 2) AS total_revenue, COUNT(oi.id) AS units_sold
FROM `{project_id}.{dataset_id}.order_items` oi
JOIN `{project_id}.{dataset_id}.products` p ON oi.product_id = p.id
GROUP BY p.name
ORDER BY total_revenue DESC
LIMIT @limit
```

#### 3. Order Status Breakdown
Fetches count of orders grouping by status.
```sql
SELECT status, COUNT(order_id) AS count
FROM `{project_id}.{dataset_id}.orders`
GROUP BY status
```

#### 4. Category Performance
Fetches category revenue and units sold.
```sql
SELECT p.category, ROUND(SUM(oi.sale_price), 2) AS total_revenue, COUNT(oi.id) AS units_sold
FROM `{project_id}.{dataset_id}.order_items` oi
JOIN `{project_id}.{dataset_id}.products` p ON oi.product_id = p.id
GROUP BY p.category
ORDER BY total_revenue DESC
```

#### 5. Dashboard Summary
Retrieves total orders, total revenue, and calculates average order value.
```sql
SELECT 
  (SELECT COUNT(order_id) FROM `{project_id}.{dataset_id}.orders`) AS total_orders,
  (SELECT ROUND(SUM(sale_price), 2) FROM `{project_id}.{dataset_id}.order_items`) AS total_revenue
```

## 6. Testing & Verification Plan
1. Initialize BigQuery client locally.
2. Query validation: Run each query inside Python shell, check schemas and values.
3. FastAPI endpoint integration: Run dashboard app locally, verify endpoint payloads manually or using curl/requests.

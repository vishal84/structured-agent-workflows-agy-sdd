# BigQuery Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the e-commerce analytics dashboard backend to query live data from BigQuery dataset `thelook_ecommerce` via `google-cloud-bigquery`, replacing local CSV reads.

**Architecture:** Initialize a BigQuery client reading configuration from `BIGQUERY_PROJECT_ID` and `BIGQUERY_DATASET_ID` environment variables. Refactor `src/data_service.py` to execute SQL aggregation queries directly against BigQuery tables (`orders`, `order_items`, `products`) and return results in the existing API schema.

**Tech Stack:** Python 3.11, FastAPI, google-cloud-bigquery, pytest, uv.

## Global Constraints
- Target Project ID: default `agents-cli-503022`
- Target Dataset ID: default `thelook_ecommerce`
- Package manager: `uv`
- Testing framework: `pytest`

---

### Task 1: Add Dependencies and Client Helper

**Files:**
- Modify: `pyproject.toml`
- Create: `src/config.py`
- Create: `tests/test_config.py`

**Interfaces:**
- Produces: `src/config.py:get_bigquery_client()` returning `google.cloud.bigquery.Client` and `get_dataset_ref()` returning formatted dataset string `project_id.dataset_id`.

- [ ] **Step 1: Write failing test for config and BQ client helper**

Create `tests/test_config.py`:
```python
import os
from src.config import get_bigquery_config

def test_get_bigquery_config_defaults():
    project_id, dataset_id = get_bigquery_config()
    assert project_id == os.getenv("BIGQUERY_PROJECT_ID", "agents-cli-503022")
    assert dataset_id == os.getenv("BIGQUERY_DATASET_ID", "thelook_ecommerce")
```

- [ ] **Step 2: Add dependencies to pyproject.toml and sync**

Update `pyproject.toml`:
```toml
[project]
name = "ecommerce-dashboard"
version = "0.1.0"
description = "E-commerce analytics dashboard with BigQuery data"
requires-python = ">=3.11"
dependencies = [
    "fastapi[standard]>=0.115.0",
    "pandas>=2.2.0",
    "jinja2>=3.1.0",
    "google-cloud-bigquery>=3.25.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "httpx>=0.27.0",
]
```

Run command:
`uv sync`

- [ ] **Step 3: Implement src/config.py**

Create `src/config.py`:
```python
import os
from google.cloud import bigquery

def get_bigquery_config() -> tuple[str, str]:
    project_id = os.getenv("BIGQUERY_PROJECT_ID", "agents-cli-503022")
    dataset_id = os.getenv("BIGQUERY_DATASET_ID", "thelook_ecommerce")
    return project_id, dataset_id

def get_bigquery_client() -> bigquery.Client:
    project_id, _ = get_bigquery_config()
    return bigquery.Client(project=project_id)

def get_table_path(table_name: str) -> str:
    project_id, dataset_id = get_bigquery_config()
    return f"`{project_id}.{dataset_id}.{table_name}`"
```

- [ ] **Step 4: Run test to verify Task 1 passes**

Run command:
`uv run pytest tests/test_config.py -v`

Expected: PASS

- [ ] **Step 5: Commit Task 1**

```bash
git add pyproject.toml uv.lock src/config.py tests/test_config.py
git commit -m "feat: add google-cloud-bigquery dependency and config helper"
```

---

### Task 2: Refactor data_service.py with BigQuery Queries

**Files:**
- Modify: `src/data_service.py`
- Create: `tests/test_data_service.py`

**Interfaces:**
- Consumes: `src/config.py:get_bigquery_client()`, `src/config.py:get_table_path()`
- Produces: `get_revenue_trend()`, `get_top_products()`, `get_order_status_breakdown()`, `get_category_performance()`, `get_dashboard_summary()` in `src/data_service.py`.

- [ ] **Step 1: Write integration tests for data_service functions**

Create `tests/test_data_service.py`:
```python
from src.data_service import (
    get_revenue_trend,
    get_top_products,
    get_order_status_breakdown,
    get_category_performance,
    get_dashboard_summary,
)

def test_get_revenue_trend():
    res = get_revenue_trend()
    assert isinstance(res, list)
    if len(res) > 0:
        assert "date" in res[0]
        assert "revenue" in res[0]

def test_get_top_products():
    res = get_top_products(limit=5)
    assert isinstance(res, list)
    assert len(res) <= 5
    if len(res) > 0:
        assert "name" in res[0]
        assert "total_revenue" in res[0]
        assert "units_sold" in res[0]

def test_get_order_status_breakdown():
    res = get_order_status_breakdown()
    assert isinstance(res, list)
    if len(res) > 0:
        assert "status" in res[0]
        assert "count" in res[0]

def test_get_category_performance():
    res = get_category_performance()
    assert isinstance(res, list)
    if len(res) > 0:
        assert "category" in res[0]
        assert "total_revenue" in res[0]
        assert "units_sold" in res[0]

def test_get_dashboard_summary():
    res = get_dashboard_summary()
    assert isinstance(res, dict)
    assert "total_orders" in res
    assert "total_revenue" in res
    assert "avg_order_value" in res
    assert res["data_source"] == "BigQuery"
```

- [ ] **Step 2: Update src/data_service.py to query BigQuery**

Replace content of `src/data_service.py`:
```python
from google.cloud import bigquery
from src.config import get_bigquery_client, get_table_path


def get_revenue_trend() -> list[dict]:
    client = get_bigquery_client()
    orders_table = get_table_path("orders")
    items_table = get_table_path("order_items")

    query = f"""
    SELECT DATE(o.created_at) AS date, ROUND(SUM(oi.sale_price), 2) AS revenue
    FROM {orders_table} o
    JOIN {items_table} oi ON o.order_id = oi.order_id
    WHERE o.status = 'Complete'
    GROUP BY date
    ORDER BY date
    """
    query_job = client.query(query)
    results = query_job.result()

    return [
        {"date": str(row["date"]), "revenue": float(row["revenue"])}
        for row in results
    ]


def get_top_products(limit: int = 10) -> list[dict]:
    client = get_bigquery_client()
    items_table = get_table_path("order_items")
    products_table = get_table_path("products")

    query = f"""
    SELECT p.name, ROUND(SUM(oi.sale_price), 2) AS total_revenue, COUNT(oi.id) AS units_sold
    FROM {items_table} oi
    JOIN {products_table} p ON oi.product_id = p.id
    GROUP BY p.name
    ORDER BY total_revenue DESC
    LIMIT @limit
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("limit", "INT64", limit)
        ]
    )
    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    return [
        {
            "name": row["name"],
            "total_revenue": float(row["total_revenue"]),
            "units_sold": int(row["units_sold"]),
        }
        for row in results
    ]


def get_order_status_breakdown() -> list[dict]:
    client = get_bigquery_client()
    orders_table = get_table_path("orders")

    query = f"""
    SELECT status, COUNT(order_id) AS count
    FROM {orders_table}
    GROUP BY status
    """
    query_job = client.query(query)
    results = query_job.result()

    return [
        {"status": row["status"], "count": int(row["count"])}
        for row in results
    ]


def get_category_performance() -> list[dict]:
    client = get_bigquery_client()
    items_table = get_table_path("order_items")
    products_table = get_table_path("products")

    query = f"""
    SELECT p.category, ROUND(SUM(oi.sale_price), 2) AS total_revenue, COUNT(oi.id) AS units_sold
    FROM {items_table} oi
    JOIN {products_table} p ON oi.product_id = p.id
    GROUP BY p.category
    ORDER BY total_revenue DESC
    """
    query_job = client.query(query)
    results = query_job.result()

    return [
        {
            "category": row["category"],
            "total_revenue": float(row["total_revenue"]),
            "units_sold": int(row["units_sold"]),
        }
        for row in results
    ]


def get_dashboard_summary() -> dict:
    client = get_bigquery_client()
    orders_table = get_table_path("orders")
    items_table = get_table_path("order_items")

    query = f"""
    SELECT 
      (SELECT COUNT(order_id) FROM {orders_table}) AS total_orders,
      (SELECT ROUND(SUM(sale_price), 2) FROM {items_table}) AS total_revenue
    """
    query_job = client.query(query)
    results = list(query_job.result())

    if results:
        row = results[0]
        total_orders = int(row["total_orders"] or 0)
        total_revenue = float(row["total_revenue"] or 0.0)
    else:
        total_orders = 0
        total_revenue = 0.0

    avg_order_value = round(total_revenue / total_orders, 2) if total_orders > 0 else 0.0

    return {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "avg_order_value": avg_order_value,
        "data_source": "BigQuery",
    }
```

- [ ] **Step 3: Run pytest to verify Task 2 passes**

Run command:
`uv run pytest tests/test_data_service.py -v`

Expected: PASS

- [ ] **Step 4: Commit Task 2**

```bash
git add src/data_service.py tests/test_data_service.py
git commit -m "feat: refactor data_service to use live BigQuery queries"
```

---

### Task 3: End-to-End API Integration Testing

**Files:**
- Create: `tests/test_main.py`

- [ ] **Step 1: Write FastAPI endpoint integration tests**

Create `tests/test_main.py`:
```python
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_read_dashboard():
    response = client.get("/")
    assert response.status_code == 200
    assert "E-commerce Analytics Dashboard" in response.text
    assert "BigQuery" in response.text

def test_api_revenue_trend():
    response = client.get("/api/revenue-trend")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_api_top_products():
    response = client.get("/api/top-products?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5

def test_api_order_status():
    response = client.get("/api/order-status")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_api_category_performance():
    response = client.get("/api/category-performance")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_api_summary():
    response = client.get("/api/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["data_source"] == "BigQuery"
```

- [ ] **Step 2: Run all tests**

Run command:
`uv run pytest -v`

Expected: PASS (all tests in test_config.py, test_data_service.py, test_main.py pass).

- [ ] **Step 3: Commit Task 3**

```bash
git add tests/test_main.py
git commit -m "test: add end-to-end API endpoint tests for BigQuery backend"
```

# E-commerce Analytics Dashboard

Companion repository for the **Spec-Driven Development with Antigravity CLI** codelab.

## What is this?

A FastAPI web app that displays e-commerce analytics — revenue trends, top products, and order status — using static CSV data. The codelab guides you through upgrading this app to query live data from BigQuery's `thelook_ecommerce` public dataset, using Antigravity CLI's spec-driven development workflow.

## Quick start

```bash
uv sync
uv run uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

Open `http://localhost:8080` to view the dashboard.

## Codelab

TODO

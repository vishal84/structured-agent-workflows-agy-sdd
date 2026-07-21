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

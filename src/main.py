from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from src.data_service import (
    get_revenue_trend,
    get_top_products,
    get_order_status_breakdown,
    get_category_performance,
    get_dashboard_summary,
)

app = FastAPI(title="E-commerce Analytics Dashboard")

app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    summary = get_dashboard_summary()
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"summary": summary},
    )


@app.get("/api/revenue-trend")
async def revenue_trend():
    return get_revenue_trend()


@app.get("/api/top-products")
async def top_products(limit: int = 10):
    return get_top_products(limit=limit)


@app.get("/api/order-status")
async def order_status():
    return get_order_status_breakdown()


@app.get("/api/category-performance")
async def category_performance():
    return get_category_performance()


@app.get("/api/summary")
async def summary():
    return get_dashboard_summary()

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

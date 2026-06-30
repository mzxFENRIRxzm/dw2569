from django.shortcuts import render
from suphasan.clickhouse import get_client


def dashboard(request):
    client = get_client()

    sales_overview = client.query('''
        SELECT
            toDate(order_date) AS day,
            countDistinct(order_id) AS orders,
            sum(final_price) AS revenue,
            sum(quantity) AS units_sold
        FROM dw_sales_fact
        GROUP BY day
        ORDER BY day DESC
        LIMIT 30
    ''').result_rows if client.query('EXISTS TABLE dw_sales_fact').result_rows[0][0] else []

    top_products = client.query('''
        SELECT
            product_name,
            sum(quantity) AS total_qty,
            sum(final_price) AS total_revenue
        FROM dw_sales_fact
        GROUP BY product_name
        ORDER BY total_revenue DESC
        LIMIT 10
    ''').result_rows if client.query('EXISTS TABLE dw_sales_fact').result_rows[0][0] else []

    low_stock = client.query('''
        SELECT product_name, sku, current_quantity, reorder_point, location
        FROM dw_stock_snapshot
        WHERE current_quantity <= reorder_point
        ORDER BY current_quantity ASC
    ''').result_rows if client.query('EXISTS TABLE dw_stock_snapshot').result_rows[0][0] else []

    inventory_summary = client.query('''
        SELECT
            log_type,
            count() AS entries,
            sum(change_quantity) AS total_change
        FROM dw_inventory_fact
        GROUP BY log_type
    ''').result_rows if client.query('EXISTS TABLE dw_inventory_fact').result_rows[0][0] else []

    active_coupons = client.query('''
        SELECT code, discount_type, value, min_purchase, end_date
        FROM dw_marketing_fact
        WHERE active = 1 AND end_date >= now()
    ''').result_rows if client.query('EXISTS TABLE dw_marketing_fact').result_rows[0][0] else []

    loyalty_summary = client.query('''
        SELECT
            count() AS total_members,
            sum(points) AS total_points,
            avg(points) AS avg_points
        FROM dw_loyalty_fact
    ''').result_rows if client.query('EXISTS TABLE dw_loyalty_fact').result_rows[0][0] else []

    shipment_status = client.query('''
        SELECT status, count() AS cnt
        FROM dw_logistics_fact
        GROUP BY status
    ''').result_rows if client.query('EXISTS TABLE dw_logistics_fact').result_rows[0][0] else []

    context = {
        'sales_overview': sales_overview,
        'top_products': top_products,
        'low_stock': low_stock,
        'inventory_summary': inventory_summary,
        'active_coupons': active_coupons,
        'loyalty_summary': loyalty_summary[0] if loyalty_summary else None,
        'shipment_status': shipment_status,
    }
    return render(request, 'analytics/dashboard.html', context)

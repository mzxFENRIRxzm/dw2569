import clickhouse_connect
from django.conf import settings

def get_client():
    """
    Returns a ClickHouse client connection based on Django settings.
    Usage:
        from suphasan.clickhouse import get_client
        client = get_client()
        result = client.query('SELECT 1')
    """
    return clickhouse_connect.get_client(
        host=settings.CLICKHOUSE_HOST,
        port=settings.CLICKHOUSE_PORT,
        username=settings.CLICKHOUSE_USER,
        password=settings.CLICKHOUSE_PASSWORD,
        database=settings.CLICKHOUSE_DB,
    )

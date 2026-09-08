from django.core.management.base import BaseCommand
from suphasan.clickhouse import get_client


class Command(BaseCommand):
    help = 'Creates ClickHouse tables for analytics'

    def handle(self, *args, **kwargs):
        client = get_client()
        self.stdout.write('Setting up ClickHouse tables...')

        client.command('''
            CREATE TABLE IF NOT EXISTS dw_sales_fact (
                order_id          UInt32,
                order_date        DateTime,
                customer_name     String,
                email             String,
                phone             String,
                product_id        UInt32,
                product_name      String,
                category          String,
                quantity          UInt32,
                unit_price        Decimal(10,2),
                total_price       Decimal(10,2),
                discount          Decimal(10,2),
                final_price       Decimal(10,2),
                payment_method    String,
                status            String
            ) ENGINE = ReplacingMergeTree()
            ORDER BY (order_id, product_id)
        ''')

        client.command('''
            CREATE TABLE IF NOT EXISTS dw_inventory_fact (
                log_id            UInt32,
                product_id        UInt32,
                product_name      String,
                change_quantity   Int32,
                log_type          String,
                reason            String,
                created_at        DateTime
            ) ENGINE = ReplacingMergeTree()
            ORDER BY (log_id)
        ''')

        client.command('''
            CREATE TABLE IF NOT EXISTS dw_stock_snapshot (
                product_id        UInt32,
                product_name      String,
                sku               String,
                current_quantity  Int32,
                reorder_point     Int32,
                location          String,
                updated_at        DateTime
            ) ENGINE = ReplacingMergeTree()
            ORDER BY (product_id)
        ''')

        client.command('''
            CREATE TABLE IF NOT EXISTS dw_marketing_fact (
                coupon_id         UInt32,
                code              String,
                discount_type     String,
                value             Decimal(10,2),
                min_purchase      Decimal(10,2),
                active            UInt8,
                start_date        DateTime,
                end_date          DateTime
            ) ENGINE = ReplacingMergeTree()
            ORDER BY (coupon_id)
        ''')

        client.command('''
            CREATE TABLE IF NOT EXISTS dw_loyalty_fact (
                account_id        UInt32,
                customer_name     String,
                phone             String,
                points            Int32,
                updated_at        DateTime
            ) ENGINE = ReplacingMergeTree()
            ORDER BY (account_id)
        ''')

        client.command('''
            CREATE TABLE IF NOT EXISTS dw_logistics_fact (
                shipment_id       UInt32,
                order_id          UInt32,
                tracking_number   String,
                carrier           String,
                shipping_cost     Decimal(10,2),
                status            String,
                updated_at        DateTime
            ) ENGINE = ReplacingMergeTree()
            ORDER BY (shipment_id)
        ''')

        client.command('''
            CREATE TABLE IF NOT EXISTS movie_ratings (
                movie_id UInt64,
                movie_title String,
                release_year UInt16,
                genre LowCardinality(String),
                rating Float32,
                vote_count UInt32,
                rated_at DateTime DEFAULT now()
            ) ENGINE = ReplacingMergeTree(rated_at)
            ORDER BY (movie_id, rated_at)
        ''')

        self.stdout.write(self.style.SUCCESS('ClickHouse tables created/verified successfully'))

from django.core.management.base import BaseCommand
from django.utils import timezone
from suphasan.clickhouse import get_client
from sale.models import Order, OrderItem, Product
from inventory.models import StockLevel, StockLog
from marketing.models import Coupon, LoyaltyAccount
from logistics.models import Shipment


class Command(BaseCommand):
    help = 'Syncs all Django data to ClickHouse analytics tables'

    def handle(self, *args, **kwargs):
        client = get_client()
        now = timezone.now()
        self.stdout.write('Syncing data to ClickHouse...')

        # Sync sales
        self.stdout.write('  Syncing sales...')
        for order in Order.objects.prefetch_related('items__product').iterator(chunk_size=100):
            for item in order.items.all():
                client.command('''
                    INSERT INTO dw_sales_fact VALUES
                    (%(order_id)s, %(order_date)s, %(customer_name)s, %(email)s,
                     %(phone)s, %(product_id)s, %(product_name)s, %(category)s,
                     %(quantity)s, %(unit_price)s, %(total_price)s, %(discount)s,
                     %(final_price)s, %(payment_method)s, %(status)s)
                ''', parameters={
                    'order_id': order.id,
                    'order_date': order.created_at.isoformat(),
                    'customer_name': order.customer_name,
                    'email': order.email,
                    'phone': order.phone,
                    'product_id': item.product.id,
                    'product_name': item.product.name,
                    'category': 'general',
                    'quantity': item.quantity,
                    'unit_price': float(item.price),
                    'total_price': float(order.total_price),
                    'discount': float(order.discount_applied),
                    'final_price': float(order.final_price),
                    'payment_method': order.payment_method,
                    'status': order.status,
                })

        # Sync inventory logs
        self.stdout.write('  Syncing inventory logs...')
        for log in StockLog.objects.select_related('product').iterator():
            client.command('''
                INSERT INTO dw_inventory_fact VALUES
                (%(log_id)s, %(product_id)s, %(product_name)s,
                 %(change_quantity)s, %(log_type)s, %(reason)s, %(created_at)s)
            ''', parameters={
                'log_id': log.id,
                'product_id': log.product.id,
                'product_name': log.product.name,
                'change_quantity': log.change_quantity,
                'log_type': log.log_type,
                'reason': log.reason,
                'created_at': log.created_at.isoformat(),
            })

        # Sync stock snapshots
        self.stdout.write('  Syncing stock snapshots...')
        for stock in StockLevel.objects.select_related('product').iterator():
            client.command('''
                INSERT INTO dw_stock_snapshot VALUES
                (%(product_id)s, %(product_name)s, %(sku)s,
                 %(current_quantity)s, %(reorder_point)s, %(location)s, %(updated_at)s)
            ''', parameters={
                'product_id': stock.product.id,
                'product_name': stock.product.name,
                'sku': stock.product.sku,
                'current_quantity': stock.quantity,
                'reorder_point': stock.reorder_point,
                'location': stock.location,
                'updated_at': now.isoformat(),
            })

        # Sync marketing
        self.stdout.write('  Syncing coupons...')
        for coupon in Coupon.objects.iterator():
            client.command('''
                INSERT INTO dw_marketing_fact VALUES
                (%(coupon_id)s, %(code)s, %(discount_type)s, %(value)s,
                 %(min_purchase)s, %(active)s, %(start_date)s, %(end_date)s)
            ''', parameters={
                'coupon_id': coupon.id,
                'code': coupon.code,
                'discount_type': coupon.discount_type,
                'value': float(coupon.value),
                'min_purchase': float(coupon.min_purchase),
                'active': 1 if coupon.active else 0,
                'start_date': coupon.start_date.isoformat(),
                'end_date': coupon.end_date.isoformat(),
            })

        # Sync loyalty
        self.stdout.write('  Syncing loyalty accounts...')
        for acc in LoyaltyAccount.objects.iterator():
            client.command('''
                INSERT INTO dw_loyalty_fact VALUES
                (%(account_id)s, %(customer_name)s, %(phone)s, %(points)s, %(updated_at)s)
            ''', parameters={
                'account_id': acc.id,
                'customer_name': acc.customer_name,
                'phone': acc.phone,
                'points': acc.points,
                'updated_at': now.isoformat(),
            })

        # Sync logistics
        self.stdout.write('  Syncing shipments...')
        for shipment in Shipment.objects.select_related('order').iterator():
            client.command('''
                INSERT INTO dw_logistics_fact VALUES
                (%(shipment_id)s, %(order_id)s, %(tracking_number)s,
                 %(carrier)s, %(shipping_cost)s, %(status)s, %(updated_at)s)
            ''', parameters={
                'shipment_id': shipment.id,
                'order_id': shipment.order.id,
                'tracking_number': shipment.tracking_number,
                'carrier': shipment.carrier,
                'shipping_cost': float(shipment.shipping_cost),
                'status': shipment.status,
                'updated_at': shipment.updated_at.isoformat(),
            })

        self.stdout.write(self.style.SUCCESS('Data sync to ClickHouse completed'))

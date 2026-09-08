-- ClickHouse Dimensional Modeling Schema for Suphasan

CREATE DATABASE IF NOT EXISTS dwh_suphasan;

USE dwh_suphasan;

-- Movie ratings dashboard fact table (one row per movie snapshot)
CREATE TABLE IF NOT EXISTS movie_ratings (
    movie_id UInt64,
    movie_title String,
    release_year UInt16,
    genre LowCardinality(String),
    rating Float32,
    vote_count UInt32,
    rated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(rated_at)
ORDER BY (movie_id, rated_at);

-- ==============================================
-- 1. Dimension Tables
-- ==============================================

-- 1.1 Date Dimension (SCD Type 0)
CREATE TABLE IF NOT EXISTS dim_date (
    date_sk Int32,
    full_date Date,
    day_of_week UInt8,
    day_name String,
    day_of_month UInt8,
    day_of_year UInt16,
    week_of_year UInt8,
    month_number UInt8,
    month_name String,
    year_quarter UInt8,
    year_number UInt16,
    is_weekend UInt8,
    is_holiday UInt8
) ENGINE = MergeTree()
ORDER BY date_sk;

-- 1.2 Product Dimension (SCD Type 2)
CREATE TABLE IF NOT EXISTS dim_product (
    product_sk Int64,
    product_id Int64, -- Natural Key from Django
    name String,
    sku String,
    price Decimal(10, 2),
    cost Decimal(10, 2),
    effective_start_date DateTime,
    effective_end_date DateTime,
    is_current UInt8
) ENGINE = MergeTree()
ORDER BY product_sk;

-- 1.3 Customer Dimension (SCD Type 1)
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_sk Int64,
    customer_id Int64, -- If available from Order/LoyaltyAccount
    phone String, -- Natural Key from Order/LoyaltyAccount
    customer_name String,
    email String,
    loyalty_points Int32
) ENGINE = MergeTree()
ORDER BY customer_sk;

-- 1.4 Coupon Dimension (SCD Type 1)
CREATE TABLE IF NOT EXISTS dim_coupon (
    coupon_sk Int64,
    coupon_id Int64, -- Natural Key
    code String,
    discount_type String,
    value Decimal(10, 2),
    min_purchase Decimal(10, 2),
    is_active UInt8
) ENGINE = MergeTree()
ORDER BY coupon_sk;

-- 1.5 Location Dimension (SCD Type 0/1)
CREATE TABLE IF NOT EXISTS dim_location (
    location_sk Int64,
    location_name String
) ENGINE = MergeTree()
ORDER BY location_sk;

-- ==============================================
-- 2. Fact Tables
-- ==============================================

-- 2.1 Fact Sales (Grain: 1 row per OrderItem)
-- Note: discount_applied must be allocated per item during ETL
CREATE TABLE IF NOT EXISTS fact_sales (
    date_sk Int32,
    product_sk Int64,
    customer_sk Int64,
    coupon_sk Int64,
    order_id Int64, -- Degenerate Dimension
    quantity UInt32,
    unit_price Decimal(10, 2),
    subtotal Decimal(10, 2),
    allocated_discount Decimal(10, 2), -- Computed in ETL: discount_applied * (subtotal / total_price)
    final_price Decimal(10, 2), -- Computed in ETL: subtotal - allocated_discount
    status String,
    payment_method String
) ENGINE = MergeTree()
ORDER BY (date_sk, product_sk, customer_sk);

-- 2.2 Fact Inventory Movements (Grain: 1 row per StockLog)
CREATE TABLE IF NOT EXISTS fact_inventory_movements (
    date_sk Int32,
    product_sk Int64,
    location_sk Int64,
    log_type String,
    change_quantity Int32,
    reason String
) ENGINE = MergeTree()
ORDER BY (date_sk, product_sk, location_sk);

-- 2.3 Fact Shipments (Grain: 1 row per Shipment)
CREATE TABLE IF NOT EXISTS fact_shipments (
    date_sk Int32,
    order_id Int64,
    customer_sk Int64,
    tracking_number String,
    carrier String,
    shipping_cost Decimal(10, 2),
    status String,
    lead_time_hours Int32
) ENGINE = MergeTree()
ORDER BY (date_sk, carrier);


-- ==============================================
-- 3. Mart Tables (Wide Tables)
-- ==============================================

-- 3.1 Sales Performance Mart (Wide Table for fast reporting)
-- Pre-joined denormalized table
CREATE TABLE IF NOT EXISTS mart_sales_performance_wide (
    -- Date attributes
    full_date Date,
    month_name String,
    year_number UInt16,
    
    -- Product attributes
    product_name String,
    product_sku String,
    
    -- Customer attributes
    customer_name String,
    
    -- Order details
    order_id Int64,
    status String,
    payment_method String,
    
    -- Metrics
    quantity UInt32,
    unit_price Decimal(10, 2),
    subtotal Decimal(10, 2),
    allocated_discount Decimal(10, 2),
    final_price Decimal(10, 2),
    cost Decimal(10, 2),
    margin Decimal(10, 2) -- Computed: final_price - (cost * quantity)
) ENGINE = MergeTree()
ORDER BY (full_date, product_sku);

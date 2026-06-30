# Top Open Source Data Warehousing Software 2026

## 1. ClickHouse
- **Stars:** ~46.7k | **License:** Apache 2.0
- Column-oriented OLAP DB with vectorized execution, sub-second queries at petabyte scale.
- Ideal for observability, real-time analytics, high-throughput event logging.
- Self-host or ClickHouse Cloud.

## 2. Apache Doris
- **Stars:** ~15.2k | **License:** Apache 2.0
- MPP real-time analytical database; unified lakehouse with Iceberg/Delta/Hudi catalogs.
- Sub-second response, high-concurrency point queries, real-time ingestion.
- Used for BI, ad-hoc, log analysis, user profiling.

## 3. StarRocks
- **Stars:** ~11.8k | **License:** Apache 2.0 (Linux Foundation)
- Fastest open query engine for sub-second analytics on/off data lakehouse.
- Native vectorized engine, real-time upsert, direct lake querying (Hive/Iceberg/Delta/Hudi).
- 3x faster than alternatives on average.

## 4. Trino (formerly PrestoSQL)
- **Stars:** ~12.9k | **License:** Apache 2.0
- Distributed SQL query engine for big data analytics.
- Federated queries across multiple data sources (Hive, Iceberg, Delta, relational DBs).
- De facto standard for open lakehouse querying alongside Iceberg + Polaris.

## 5. Presto
- **Stars:** ~16.7k | **License:** Apache 2.0
- Original distributed SQL query engine from Facebook.
- C++ native execution via Velox for improved performance.
- Broad adoption in large-scale data platforms.

## 6. Apache Druid
- **Stars:** ~13.5k | **License:** Apache 2.0
- Real-time OLAP database designed for fast aggregations and time-series.
- Best for streaming ingestion, event-driven analytics, observability dashboards.

## 7. Apache Pinot
- **Stars:** ~2.6k (LinkedIn) | **License:** Apache 2.0
- Real-time OLAP with extreme concurrency for user-facing analytics.
- Supports offline and near-real-time ingestion; integrates with Kafka.

## 8. Databend
- **Stars:** ~9.2k | **License:** Apache 2.0 + Elastic 2.0
- Cloud-native data warehouse built in Rust.
- Analytics + vector search + full-text search unified; agent-ready with sandbox UDFs.
- Git-like branching for safe data experimentation.

## 9. Apache Kylin
- **Stars:** ~3.7k | **License:** Apache 2.0
- OLAP engine with pre-computed cubes for sub-second latency on trillions of records.
- Seamless BI tool integration; star/snowflake schema modeling.
- Mature enterprise option for predefined, high-concurrency analytics.

## 10. DuckDB
- **Stars:** ~28k | **License:** MIT
- Embedded in-process OLAP database. No server needed.
- Ideal for fast analytical queries on small-to-medium data, data science, local dev.
- MotherDuck: cloud-managed DuckDB with serverless scale.

## 11. WarehousePG (WHPG)
- **Stars:** ~100 | **License:** Apache 2.0
- Open-source continuation of Greenplum (based on PostgreSQL).
- MPP data warehouse for petabyte-scale analytics.
- Born from Greenplum going closed-source in 2024.

## 12. Apache Hive
- **Stars:** ~5.4k | **License:** Apache 2.0
- Data warehouse infrastructure on Hadoop.
- SQL-like queries (HiveQL) on large datasets stored in HDFS.
- Legacy but still widely deployed in Hadoop ecosystems.

---

### Quick Picks by Use Case

| Use Case | Recommendation |
|---|---|
| Real-time / sub-second OLAP | ClickHouse, StarRocks, Apache Doris |
| Open lakehouse querying | Trino + Iceberg + Polaris |
| Cloud-native / Rust-based | Databend |
| Embedded analytics (small data) | DuckDB |
| Predefined cube-based analytics | Apache Kylin |
| Streaming / time-series | Apache Druid, Apache Pinot |
| Hadoop ecosystem | Apache Hive |
| Petabyte MPP | WarehousePG (Greenplum fork) |

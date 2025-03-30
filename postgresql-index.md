# Creating and Verifying Indexes in PostgreSQL

## Creating Indexes in PostgreSQL

### Basic Index Creation Syntax
```sql
CREATE INDEX index_name ON table_name (column_name);
```

### Common Index Types

1. **B-tree (default, good for most cases)**
   ```sql
   CREATE INDEX idx_customer_name ON customers (last_name);
   ```

2. **Hash (good for equality comparisons)**
   ```sql
   CREATE INDEX idx_product_id_hash ON products USING HASH (product_id);
   ```

3. **GIN (Generalized Inverted Index, good for array/JSON data)**
   ```sql
   CREATE INDEX idx_product_tags ON products USING GIN (tags);
   ```

4. **GiST (Geometric/Full-text search)**
   ```sql
   CREATE INDEX idx_geom ON spatial_data USING GIST (geom);
   ```

5. **BRIN (Block Range Index, good for large sorted tables)**
   ```sql
   CREATE INDEX idx_sensor_readings ON sensor_data USING BRIN (timestamp);
   ```

### Multi-column Indexes
```sql
CREATE INDEX idx_customer_name_email ON customers (last_name, email);
```

### Partial Indexes (index only some rows)
```sql
CREATE INDEX idx_active_users ON users (email) WHERE is_active = true;
```

### Unique Indexes
```sql
CREATE UNIQUE INDEX idx_unique_email ON users (email);
```

## Verifying Index Usage

### 1. Using EXPLAIN to Check Index Usage
```sql
EXPLAIN ANALYZE SELECT * FROM customers WHERE last_name = 'Smith';
```

Look for lines like:
```
Index Scan using idx_customer_name on customers
```

### 2. Checking Existing Indexes
```sql
-- List all indexes in database
SELECT tablename, indexname, indexdef 
FROM pg_indexes 
WHERE schemaname = 'public';

-- For a specific table
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'customers';
```

### 3. Checking Index Usage Statistics
```sql
SELECT 
    schemaname || '.' || relname AS table,
    indexrelname AS index,
    idx_scan AS scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

### 4. Forcing Index Usage (for testing)
```sql
-- Temporarily disable sequential scans to force index usage
SET enable_seqscan = OFF;

-- Run your query
EXPLAIN ANALYZE SELECT * FROM customers WHERE last_name = 'Smith';

-- Remember to re-enable
SET enable_seqscan = ON;
```

## Best Practices

1. **Index columns frequently used in WHERE clauses**
2. **Consider indexes for JOIN columns**
3. **Don't over-index - each index adds write overhead**
4. **For large tables, consider CONCURRENTLY option to avoid locking**
   ```sql
   CREATE INDEX CONCURRENTLY idx_large_table ON large_table (column_name);
   ```
5. **Regularly monitor index usage and remove unused indexes**
6. **Consider index-only scans by including all needed columns**
   ```sql
   CREATE INDEX idx_covering ON orders (customer_id) INCLUDE (order_date, total);
   ```

## Example Workflow

1. **Identify slow query**:
   ```sql
   SELECT * FROM orders WHERE customer_id = 123 AND order_date > '2023-01-01';
   ```

2. **Check current execution plan**:
   ```sql
   EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 123 AND order_date > '2023-01-01';
   ```

3. **Create appropriate index**:
   ```sql
   CREATE INDEX idx_orders_customer_date ON orders (customer_id, order_date);
   ```

4. **Verify improvement**:
   ```sql
   EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 123 AND order_date > '2023-01-01';
   ```

5. **Monitor usage over time**:
   ```sql
   SELECT * FROM pg_stat_user_indexes WHERE indexrelname = 'idx_orders_customer_date';
   ```

Remember that while indexes can dramatically improve read performance, they do add overhead to write operations (INSERT, UPDATE, DELETE), so they should be used judiciously.
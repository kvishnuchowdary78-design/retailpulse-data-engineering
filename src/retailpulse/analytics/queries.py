
-- 1. Overall sales performance
SELECT
    COUNT(*) AS total_order_lines,
    SUM(quantity) AS total_units_sold,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(AVG(revenue), 2) AS average_line_revenue
FROM fact_sales;


-- 2. Revenue by product
SELECT
    p.product_name,
    p.category,
    SUM(f.quantity) AS units_sold,
    ROUND(SUM(f.revenue), 2) AS total_revenue
FROM fact_sales f
JOIN dim_product p
    ON f.product_id = p.product_id
GROUP BY p.product_name, p.category
ORDER BY total_revenue DESC;


-- 3. Top 10 customers by revenue
SELECT
    c.customer_id,
    c.customer_name,
    c.city,
    ROUND(SUM(f.revenue), 2) AS total_revenue
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name, c.city
ORDER BY total_revenue DESC
LIMIT 10;


-- 4. Daily sales
SELECT
    d.full_date,
    COUNT(*) AS order_lines,
    ROUND(SUM(f.revenue), 2) AS daily_revenue
FROM fact_sales f
JOIN dim_date d
    ON f.date_key = d.date_key
GROUP BY d.full_date
ORDER BY d.full_date;


-- 5. Late-arriving order count
SELECT
    COUNT(*) AS late_arriving_orders
FROM fact_sales
WHERE is_late_arriving = TRUE;

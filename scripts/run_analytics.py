
from pathlib import Path
import duckdb


def main():
    root = Path(__file__).resolve().parents[1]
    db_path = root / "database" / "retailpulse.duckdb"

    connection = duckdb.connect(str(db_path), read_only=True)

    queries = {
        "OVERALL SALES": """
            SELECT
                COUNT(*) AS total_order_lines,
                SUM(quantity) AS total_units_sold,
                ROUND(SUM(revenue), 2) AS total_revenue,
                ROUND(AVG(revenue), 2) AS average_line_revenue
            FROM fact_sales
        """,
        "REVENUE BY PRODUCT": """
            SELECT
                p.product_name,
                p.category,
                SUM(f.quantity) AS units_sold,
                ROUND(SUM(f.revenue), 2) AS total_revenue
            FROM fact_sales f
            JOIN dim_product p
                ON f.product_id = p.product_id
            GROUP BY p.product_name, p.category
            ORDER BY total_revenue DESC
        """,
        "TOP 10 CUSTOMERS": """
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
            LIMIT 10
        """,
        "LATE ARRIVING ORDERS": """
            SELECT COUNT(*) AS late_arriving_orders
            FROM fact_sales
            WHERE is_late_arriving = TRUE
        """
    }

    try:
        for title, query in queries.items():
            print(f"\n{'=' * 50}")
            print(title)
            print("=" * 50)
            print(connection.execute(query).df().to_string(index=False))
    finally:
        connection.close()


if __name__ == "__main__":
    main()

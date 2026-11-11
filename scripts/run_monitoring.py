
from pathlib import Path
import json
import duckdb


def main():
    root = Path(__file__).resolve().parents[1]
    db_path = root / "database" / "retailpulse.duckdb"
    report_path = root / "outputs" / "validation_report.json"

    with open(report_path, "r", encoding="utf-8") as file:
        validation = json.load(file)

    connection = duckdb.connect(str(db_path), read_only=True)

    checks = []

    def add_check(name, passed, details):
        checks.append({
            "check": name,
            "status": "PASS" if passed else "FAIL",
            "details": str(details)
        })

    try:
        # 1. Warehouse row count reconciliation
        fact_count = connection.execute(
            "SELECT COUNT(*) FROM fact_sales"
        ).fetchone()[0]

        expected_count = validation["accepted_orders"]

        add_check(
            "Accepted orders vs warehouse fact rows",
            fact_count == expected_count,
            f"Expected {expected_count}, found {fact_count}"
        )

        # 2. Duplicate fact keys
        duplicate_count = connection.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT order_id, line_id
                FROM fact_sales
                GROUP BY order_id, line_id
                HAVING COUNT(*) > 1
            ) duplicates
        """).fetchone()[0]

        add_check(
            "Duplicate fact keys",
            duplicate_count == 0,
            f"Duplicate keys found: {duplicate_count}"
        )

        # 3. Null checks
        null_count = connection.execute("""
            SELECT COUNT(*)
            FROM fact_sales
            WHERE order_id IS NULL
               OR line_id IS NULL
               OR customer_id IS NULL
               OR product_id IS NULL
               OR revenue IS NULL
        """).fetchone()[0]

        add_check(
            "Required fact fields",
            null_count == 0,
            f"Rows with missing required values: {null_count}"
        )

        # 4. Customer references
        missing_customers = connection.execute("""
            SELECT COUNT(*)
            FROM fact_sales f
            LEFT JOIN dim_customer c
                ON f.customer_id = c.customer_id
            WHERE c.customer_id IS NULL
        """).fetchone()[0]

        add_check(
            "Customer referential integrity",
            missing_customers == 0,
            f"Missing customer references: {missing_customers}"
        )

        # 5. Product references
        missing_products = connection.execute("""
            SELECT COUNT(*)
            FROM fact_sales f
            LEFT JOIN dim_product p
                ON f.product_id = p.product_id
            WHERE p.product_id IS NULL
        """).fetchone()[0]

        add_check(
            "Product referential integrity",
            missing_products == 0,
            f"Missing product references: {missing_products}"
        )

        # 6. Revenue calculation
        revenue_mismatches = connection.execute("""
            SELECT COUNT(*)
            FROM fact_sales
            WHERE ABS(revenue - (quantity * unit_price)) > 0.01
        """).fetchone()[0]

        add_check(
            "Revenue calculation",
            revenue_mismatches == 0,
            f"Revenue mismatches: {revenue_mismatches}"
        )

        # 7. Accepted + rejected reconciliation
        input_count = validation["input_orders"]
        accepted_count = validation["accepted_orders"]
        rejected_count = validation["rejected_orders"]

        add_check(
            "Input order reconciliation",
            input_count == accepted_count + rejected_count,
            f"Input: {input_count}, accepted: {accepted_count}, "
            f"rejected: {rejected_count}"
        )

        failed = sum(
            check["status"] == "FAIL" for check in checks
        )

        result = {
            "status": "PASS" if failed == 0 else "FAIL",
            "total_checks": len(checks),
            "passed_checks": len(checks) - failed,
            "failed_checks": failed,
            "checks": checks
        }

        output_path = root / "outputs" / "monitoring_report.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(result, file, indent=4)

        print("\nRETAILPULSE DATA QUALITY MONITORING")
        print("=" * 50)

        for check in checks:
            print(
                f"{check['status']}: {check['check']}"
            )
            print(f"  {check['details']}")

        print("\nSUMMARY")
        print(f"Total checks: {result['total_checks']}")
        print(f"Passed: {result['passed_checks']}")
        print(f"Failed: {result['failed_checks']}")
        print(f"Overall status: {result['status']}")
        print(f"Report saved: {output_path}")

        if failed:
            raise SystemExit("Data quality monitoring failed.")

    finally:
        connection.close()


if __name__ == "__main__":
    main()

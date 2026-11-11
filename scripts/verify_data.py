
import csv
import json
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Input file locations
ORDERS_FILE = PROJECT_ROOT / "data" / "raw" / "orders.csv"
CUSTOMERS_FILE = PROJECT_ROOT / "data" / "raw" / "customers.json"


def verify_orders():
    """Check that the orders CSV exists and has the expected columns."""

    print("\nChecking orders.csv...")

    if not ORDERS_FILE.exists():
        raise FileNotFoundError(f"Missing file: {ORDERS_FILE}")

    expected_columns = {
        "order_id",
        "line_id",
        "customer_id",
        "product_id",
        "product_name",
        "category",
        "order_timestamp",
        "quantity",
        "unit_price"
    }

    with ORDERS_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        actual_columns = set(reader.fieldnames or [])

        if actual_columns != expected_columns:
            raise ValueError(
                f"Unexpected CSV columns. Found: {actual_columns}"
            )

        rows = list(reader)

    print(f"Orders file: FOUND")
    print(f"Order records: {len(rows)}")
    print(f"CSV columns: {len(actual_columns)}")

    return rows


def verify_customers():
    """Check that the customers JSON exists and is readable."""

    print("\nChecking customers.json...")

    if not CUSTOMERS_FILE.exists():
        raise FileNotFoundError(f"Missing file: {CUSTOMERS_FILE}")

    with CUSTOMERS_FILE.open("r", encoding="utf-8") as file:
        customers = json.load(file)

    if not isinstance(customers, list):
        raise ValueError("Customers JSON must contain a list.")

    required_fields = {
        "customer_id",
        "customer_name",
        "email",
        "city",
        "registration_date"
    }

    for index, customer in enumerate(customers):
        if not isinstance(customer, dict):
            raise ValueError(f"Customer record {index} is not an object.")

        missing = required_fields - set(customer.keys())

        if missing:
            raise ValueError(
                f"Customer record {index} is missing: {missing}"
            )

    print("Customers file: FOUND")
    print(f"Customer records: {len(customers)}")

    return customers


def main():
    print("=" * 45)
    print("       RETAILPULSE DATA VERIFICATION")
    print("=" * 45)

    orders = verify_orders()
    customers = verify_customers()

    print("\n" + "=" * 45)
    print("DATA VERIFICATION SUCCESSFUL")
    print(f"Total order records: {len(orders)}")
    print(f"Total customer records: {len(customers)}")
    print("=" * 45)


if __name__ == "__main__":
    main()

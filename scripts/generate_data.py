
import argparse
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd


PRODUCTS = [
    ("P001", "Laptop", "Electronics", 55000),
    ("P002", "Monitor", "Electronics", 12000),
    ("P003", "Keyboard", "Accessories", 1200),
    ("P004", "Mouse", "Accessories", 750),
    ("P005", "Desk", "Furniture", 8000),
]

CITIES = ["Bengaluru", "Hyderabad", "Mumbai", "Pune", "Chennai"]


def generate_customers(rng, count):
    customers = []

    for number in range(1, count + 1):
        customers.append({
            "customer_id": f"C{number:05d}",
            "customer_name": f"Customer {number}",
            "email": f"customer{number}@example.com",
            "city": rng.choice(CITIES),
            "registration_date": (
                datetime(2025, 1, 1)
                + timedelta(days=rng.randint(0, 365))
            ).date().isoformat(),
        })

    return customers


def generate_orders(rng, count, customers):
    customer_ids = [
        customer["customer_id"]
        for customer in customers
    ]

    orders = []

    data_start = datetime(
        2026, 11, 1, 0, 0,
        tzinfo=timezone.utc
    )

    window_minutes = 10 * 24 * 60

    for number in range(1, count + 1):
        product = rng.choice(PRODUCTS)

        timestamp = data_start + timedelta(
            minutes=rng.randint(0, window_minutes)
        )

        orders.append({
            "order_id": f"O{number:08d}",
            "line_id": 1,
            "customer_id": rng.choice(customer_ids),
            "product_id": product[0],
            "product_name": product[1],
            "category": product[2],
            "order_timestamp": (
                timestamp.isoformat().replace("+00:00", "Z")
            ),
            "quantity": rng.randint(1, 5),
            "unit_price": f"{product[3]:.2f}",
        })

    return orders


def add_edge_cases(orders, customers):
    if len(orders) < 6:
        raise ValueError("Generate at least 6 orders.")

    # 1. Duplicate order line: intentionally reuses the original key
    duplicate = orders[0].copy()
    orders.append(duplicate)

    # 2. Missing customer ID: unique order key
    missing_customer = orders[1].copy()
    missing_customer["order_id"] = "O_MISSING_CUSTOMER_001"
    missing_customer["customer_id"] = ""
    orders.append(missing_customer)

    # 3. Negative quantity: unique order key
    negative_quantity = orders[2].copy()
    negative_quantity["order_id"] = "O_NEGATIVE_QTY_001"
    negative_quantity["quantity"] = -2
    orders.append(negative_quantity)

    # 4. Unknown customer: unique order key
    unknown_customer = orders[3].copy()
    unknown_customer["order_id"] = "O_UNKNOWN_CUSTOMER_001"
    unknown_customer["customer_id"] = "C99999"
    orders.append(unknown_customer)

    # 5. Late-arriving but otherwise valid order
    late_order = orders[4].copy()
    late_order["order_id"] = "O_LATE_001"
    late_order["customer_id"] = customers[0]["customer_id"]
    late_order["order_timestamp"] = "2026-10-01T00:00:00Z"
    orders.append(late_order)

    # 6. Invalid product: unique order key
    invalid_product = orders[5].copy()
    invalid_product["order_id"] = "O_INVALID_PRODUCT_001"
    invalid_product["product_id"] = "P999"
    orders.append(invalid_product)

    return orders


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--orders",
        type=int,
        default=100
    )

    parser.add_argument(
        "--customers",
        type=int,
        default=1000
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42
    )

    args = parser.parse_args()

    if args.orders < 6:
        parser.error("--orders must be at least 6.")

    if args.customers < 1:
        parser.error("--customers must be at least 1.")

    rng = random.Random(args.seed)

    project_root = Path(__file__).resolve().parents[1]

    raw_dir = project_root / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    customers = generate_customers(
        rng,
        args.customers
    )

    orders = generate_orders(
        rng,
        args.orders,
        customers
    )

    orders = add_edge_cases(
        orders,
        customers
    )

    orders_path = raw_dir / "orders.csv"
    customers_path = raw_dir / "customers.json"

    pd.DataFrame(orders).to_csv(
        orders_path,
        index=False
    )

    with open(customers_path, "w", encoding="utf-8") as file:
        json.dump(
            customers,
            file,
            indent=2
        )

    print(f"Order records generated: {len(orders)}")
    print(f"Customer records generated: {len(customers)}")
    print(f"CSV file: {orders_path}")
    print(f"JSON file: {customers_path}")


if __name__ == "__main__":
    main()

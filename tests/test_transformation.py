
import pandas as pd
import pytest

from retailpulse.transformation.transform import (
    transform_customers,
    transform_products,
    transform_dates,
    transform_sales,
    transform_all,
)


def sample_customers():
    return pd.DataFrame([
        {
            "customer_id": " C001 ",
            "customer_name": " Customer One ",
            "email": "one@example.com",
            "city": " Bengaluru ",
            "registration_date": "2025-01-15",
        },
        {
            "customer_id": "C001",
            "customer_name": "Duplicate Customer",
            "email": "duplicate@example.com",
            "city": "Mysuru",
            "registration_date": "2025-02-15",
        },
        {
            "customer_id": "C002",
            "customer_name": "Customer Two",
            "email": "two@example.com",
            "city": "Hyderabad",
            "registration_date": "2025-03-10",
        },
    ])


def sample_orders():
    return pd.DataFrame([
        {
            "order_id": "O001",
            "line_id": 1,
            "customer_id": "C001",
            "product_id": "P001",
            "product_name": "Laptop",
            "category": "Electronics",
            "order_timestamp": "2026-11-01T10:00:00Z",
            "quantity": 2,
            "unit_price": 1000.0,
            "is_late_arriving": False,
            "source_file": "orders.csv",
            "source_record": 2,
        },
        {
            "order_id": "O002",
            "line_id": 1,
            "customer_id": "C002",
            "product_id": "P001",
            "product_name": "Laptop",
            "category": "Electronics",
            "order_timestamp": "2026-11-02T12:00:00Z",
            "quantity": 3,
            "unit_price": 1000.0,
            "is_late_arriving": True,
            "source_file": "orders.csv",
            "source_record": 3,
        },
        {
            "order_id": "O003",
            "line_id": 1,
            "customer_id": "C001",
            "product_id": "P002",
            "product_name": "Mouse",
            "category": "Accessories",
            "order_timestamp": "2026-11-02T15:00:00Z",
            "quantity": 2,
            "unit_price": 500.0,
            "is_late_arriving": False,
            "source_file": "orders.csv",
            "source_record": 4,
        },
    ])


def test_customer_dimension_trims_values_and_removes_duplicates():
    result = transform_customers(sample_customers())

    assert len(result) == 2
    assert result.iloc[0]["customer_id"] == "C001"
    assert result.iloc[0]["customer_name"] == "Customer One"
    assert result.iloc[0]["city"] == "Bengaluru"


def test_product_dimension_removes_duplicate_products():
    result = transform_products(sample_orders())

    assert len(result) == 2
    assert set(result["product_id"]) == {"P001", "P002"}
    assert "observed_unit_price" in result.columns
    assert "unit_price" not in result.columns


def test_date_dimension_creates_unique_date_keys():
    result = transform_dates(sample_orders())

    assert len(result) == 2
    assert set(result["date_key"]) == {20261101, 20261102}
    assert set(result["year"]) == {2026}
    assert set(result["month"]) == {11}
    assert set(result["quarter"]) == {4}


def test_sales_fact_calculates_revenue_correctly():
    result = transform_sales(sample_orders(), "test-run-001")

    assert len(result) == 3
    assert result["revenue"].tolist() == [
        2000.0,
        3000.0,
        1000.0,
    ]
    assert result["quantity"].dtype == "int64"


def test_sales_fact_preserves_run_and_source_metadata():
    result = transform_sales(sample_orders(), "test-run-001")

    assert set(result["run_id"]) == {"test-run-001"}
    assert set(result["source_file"]) == {"orders.csv"}
    assert result["source_record"].tolist() == [2, 3, 4]
    assert result["is_late_arriving"].tolist() == [
        False,
        True,
        False,
    ]


def test_sales_fact_creates_date_key_from_timestamp():
    result = transform_sales(sample_orders(), "test-run-001")

    assert result["date_key"].tolist() == [
        20261101,
        20261102,
        20261102,
    ]


def test_transformation_rejects_invalid_timestamp():
    orders = sample_orders()
    orders.loc[0, "order_timestamp"] = "not-a-date"

    with pytest.raises((ValueError, TypeError)):
        transform_sales(orders, "test-run-001")


def test_transform_all_returns_four_warehouse_tables():
    result = transform_all(
        sample_orders(),
        sample_customers(),
        "test-run-001",
    )

    assert set(result.keys()) == {
        "dim_customer",
        "dim_product",
        "dim_date",
        "fact_sales",
    }

    assert len(result["dim_customer"]) == 2
    assert len(result["dim_product"]) == 2
    assert len(result["dim_date"]) == 2
    assert len(result["fact_sales"]) == 3

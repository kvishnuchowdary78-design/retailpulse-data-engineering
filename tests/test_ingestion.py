
import json

import pandas as pd
import pytest

from retailpulse.ingestion.loader import (
    DataIngestionError,
    DataLoader,
)


ORDER_COLUMNS = [
    "order_id",
    "line_id",
    "customer_id",
    "product_id",
    "product_name",
    "category",
    "order_timestamp",
    "quantity",
    "unit_price",
]

CUSTOMER_COLUMNS = [
    "customer_id",
    "customer_name",
    "email",
    "city",
    "registration_date",
]


def create_sample_sources(root):
    root.mkdir(parents=True, exist_ok=True)

    orders = pd.DataFrame([{
        "order_id": "O001",
        "line_id": 1,
        "customer_id": "C001",
        "product_id": "P001",
        "product_name": "Laptop",
        "category": "Electronics",
        "order_timestamp": "2026-11-01T10:00:00Z",
        "quantity": 2,
        "unit_price": 1000.0,
    }], columns=ORDER_COLUMNS)

    customers = [{
        "customer_id": "C001",
        "customer_name": "Customer One",
        "email": "customer@example.com",
        "city": "Bengaluru",
        "registration_date": "2025-01-01",
    }]

    orders.to_csv(root / "orders.csv", index=False)

    with (root / "customers.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(customers, file)


def test_load_orders_success(tmp_path):
    create_sample_sources(tmp_path)

    loader = DataLoader(tmp_path)
    orders = loader.load_orders()

    assert len(orders) == 1
    assert orders.iloc[0]["order_id"] == "O001"
    assert orders.iloc[0]["source_file"] == "orders.csv"


def test_load_customers_success(tmp_path):
    create_sample_sources(tmp_path)

    loader = DataLoader(tmp_path)
    customers = loader.load_customers()

    assert len(customers) == 1
    assert customers.iloc[0]["customer_id"] == "C001"
    assert customers.iloc[0]["source_file"] == "customers.json"


def test_load_all_returns_data_and_metrics(tmp_path):
    create_sample_sources(tmp_path)

    loader = DataLoader(tmp_path)
    orders, customers, metrics = loader.load_all()

    assert len(orders) == 1
    assert len(customers) == 1
    assert metrics["order_count"] == 1
    assert metrics["customer_count"] == 1
    assert metrics["status"] == "SUCCESS"


def test_missing_orders_file_raises_error(tmp_path):
    loader = DataLoader(tmp_path)

    with pytest.raises(DataIngestionError, match="Orders file not found"):
        loader.load_orders()


def test_missing_customers_file_raises_error(tmp_path):
    loader = DataLoader(tmp_path)

    with pytest.raises(
        DataIngestionError,
        match="Customers file not found"
    ):
        loader.load_customers()


def test_invalid_orders_schema_raises_error(tmp_path):
    tmp_path.mkdir(parents=True, exist_ok=True)

    pd.DataFrame({
        "order_id": ["O001"],
        "wrong_column": ["value"],
    }).to_csv(tmp_path / "orders.csv", index=False)

    loader = DataLoader(tmp_path)

    with pytest.raises(
        DataIngestionError,
        match="Orders CSV schema"
    ):
        loader.load_orders()


def test_invalid_customers_schema_raises_error(tmp_path):
    tmp_path.mkdir(parents=True, exist_ok=True)

    with (tmp_path / "customers.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump([{"customer_id": "C001"}], file)

    loader = DataLoader(tmp_path)

    with pytest.raises(
        DataIngestionError,
        match="Customers JSON schema"
    ):
        loader.load_customers()


def test_malformed_customers_json_raises_error(tmp_path):
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "customers.json").write_text(
        "{invalid json",
        encoding="utf-8"
    )

    loader = DataLoader(tmp_path)

    with pytest.raises(
        DataIngestionError,
        match="Unable to read customers JSON"
    ):
        loader.load_customers()


def test_customers_json_must_contain_list(tmp_path):
    tmp_path.mkdir(parents=True, exist_ok=True)

    (tmp_path / "customers.json").write_text(
        '{"customer_id": "C001"}',
        encoding="utf-8"
    )

    loader = DataLoader(tmp_path)

    with pytest.raises(
        DataIngestionError,
        match="must contain a list"
    ):
        loader.load_customers()

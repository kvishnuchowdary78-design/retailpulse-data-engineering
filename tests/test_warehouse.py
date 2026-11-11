import duckdb
import pandas as pd
import pytest

from retailpulse.warehouse.loader import WarehouseLoader


def create_sample_parquet_files(root):
    warehouse_dir = root / "data" / "processed" / "warehouse"
    warehouse_dir.mkdir(parents=True)

    sample_tables = {
        "dim_customer": pd.DataFrame({
            "customer_id": ["C001"]
        }),
        "dim_product": pd.DataFrame({
            "product_id": ["P001"]
        }),
        "dim_date": pd.DataFrame({
            "date_key": [20261101]
        }),
        "fact_sales": pd.DataFrame({
            "order_id": ["O001", "O002"],
            "line_id": [1, 1],
            "revenue": [1000.0, 2000.0]
        })
    }

    for name, dataframe in sample_tables.items():
        dataframe.to_parquet(
            warehouse_dir / f"{name}.parquet",
            index=False
        )


def test_warehouse_loads_all_tables(tmp_path):
    create_sample_parquet_files(tmp_path)

    loader = WarehouseLoader(tmp_path)
    loader.load_tables()

    connection = duckdb.connect(
        str(tmp_path / "database" / "retailpulse.duckdb"),
        read_only=True
    )

    try:
        expected_counts = {
            "dim_customer": 1,
            "dim_product": 1,
            "dim_date": 1,
            "fact_sales": 2
        }

        for table, expected in expected_counts.items():
            actual = connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            assert actual == expected
    finally:
        connection.close()


def test_warehouse_rerun_does_not_duplicate_rows(tmp_path):
    create_sample_parquet_files(tmp_path)

    loader = WarehouseLoader(tmp_path)

    loader.load_tables()
    loader.load_tables()

    connection = duckdb.connect(
        str(tmp_path / "database" / "retailpulse.duckdb"),
        read_only=True
    )

    try:
        fact_count = connection.execute(
            "SELECT COUNT(*) FROM fact_sales"
        ).fetchone()[0]

        assert fact_count == 2
    finally:
        connection.close()


def test_failed_load_rolls_back_all_table_replacements(tmp_path):
    create_sample_parquet_files(tmp_path)

    loader = WarehouseLoader(tmp_path)

    # Establish the original warehouse state.
    loader.load_tables()

    warehouse_dir = tmp_path / "data" / "processed" / "warehouse"

    # Change the first table's source so we can detect a partial update.
    pd.DataFrame({
        "customer_id": ["C999"]
    }).to_parquet(
        warehouse_dir / "dim_customer.parquet",
        index=False
    )

    # Remove the second table's source to force the load to fail.
    (warehouse_dir / "dim_product.parquet").unlink()

    with pytest.raises(duckdb.Error):
        loader.load_tables()

    # Verify that the original warehouse state was preserved.
    connection = duckdb.connect(
        str(tmp_path / "database" / "retailpulse.duckdb"),
        read_only=True
    )

    try:
        customer_id = connection.execute(
            "SELECT customer_id FROM dim_customer"
        ).fetchone()[0]

        product_id = connection.execute(
            "SELECT product_id FROM dim_product"
        ).fetchone()[0]

        fact_count = connection.execute(
            "SELECT COUNT(*) FROM fact_sales"
        ).fetchone()[0]

        assert customer_id == "C001"
        assert product_id == "P001"
        assert fact_count == 2
    finally:
        connection.close()
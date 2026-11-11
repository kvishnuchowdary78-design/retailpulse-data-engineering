
from pathlib import Path
import duckdb


class WarehouseLoader:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.database_path = (
            self.project_root / "database" / "retailpulse.duckdb"
        )
        self.parquet_dir = (
            self.project_root / "data" / "processed" / "warehouse"
        )

    def load_tables(self):
        self.database_path.parent.mkdir(
            parents=True, exist_ok=True
        )

        connection = duckdb.connect(str(self.database_path))

        tables = {
            "dim_customer": "dim_customer.parquet",
            "dim_product": "dim_product.parquet",
            "dim_date": "dim_date.parquet",
            "fact_sales": "fact_sales.parquet",
        }

        try:
            for table_name, filename in tables.items():
                parquet_path = (
                    self.parquet_dir / filename
                ).as_posix().replace("'", "''")

                connection.execute(
                    f"""
                    CREATE OR REPLACE TABLE {table_name} AS
                    SELECT * FROM read_parquet('{parquet_path}')
                    """
                )

                count = connection.execute(
                    f"SELECT COUNT(*) FROM {table_name}"
                ).fetchone()[0]

                print(f"{table_name}: {count} rows loaded")

            print("\nWAREHOUSE LOAD COMPLETED")

        finally:
            connection.close()

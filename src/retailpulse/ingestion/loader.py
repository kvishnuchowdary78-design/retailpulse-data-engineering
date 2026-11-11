
import json
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd


class DataIngestionError(Exception):
    """Raised when source data cannot be ingested."""
    pass


class DataLoader:
    """Load orders and customers from CSV and JSON sources."""

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

    def __init__(self, raw_directory):
        self.raw_directory = Path(raw_directory)

    def load_orders(self):
        file_path = self.raw_directory / "orders.csv"

        if not file_path.exists():
            raise DataIngestionError(
                f"Orders file not found: {file_path}"
            )

        try:
            df = pd.read_csv(
                file_path,
                dtype={
                    "order_id": "string",
                    "customer_id": "string",
                    "product_id": "string",
                    "product_name": "string",
                    "category": "string",
                },
                encoding="utf-8-sig",
            )

            if list(df.columns) != self.ORDER_COLUMNS:
                raise DataIngestionError(
                    "Orders CSV schema does not match expected columns."
                )

            df["source_file"] = file_path.name

            print(
                f"Loaded {len(df)} order records "
                f"from {file_path.name}"
            )

            return df

        except DataIngestionError:
            raise

        except Exception as exc:
            raise DataIngestionError(
                f"Unable to read orders CSV: {exc}"
            ) from exc

    def load_customers(self):
        file_path = self.raw_directory / "customers.json"

        if not file_path.exists():
            raise DataIngestionError(
                f"Customers file not found: {file_path}"
            )

        try:
            with file_path.open(
                "r",
                encoding="utf-8"
            ) as file:
                records = json.load(file)

            if not isinstance(records, list):
                raise DataIngestionError(
                    "Customers JSON must contain a list."
                )

            df = pd.DataFrame(records)

            if list(df.columns) != self.CUSTOMER_COLUMNS:
                raise DataIngestionError(
                    "Customers JSON schema does not match expected columns."
                )

            df["source_file"] = file_path.name

            print(
                f"Loaded {len(df)} customer records "
                f"from {file_path.name}"
            )

            return df

        except DataIngestionError:
            raise

        except Exception as exc:
            raise DataIngestionError(
                f"Unable to read customers JSON: {exc}"
            ) from exc

    def load_all(self):
        """Load both sources and return their DataFrames."""

        start_time = datetime.now(timezone.utc)

        print("\nRETAILPULSE DATA INGESTION")
        print("=" * 40)

        orders = self.load_orders()
        customers = self.load_customers()

        end_time = datetime.now(timezone.utc)

        metrics = {
            "started_at": start_time.isoformat(),
            "ended_at": end_time.isoformat(),
            "order_count": len(orders),
            "customer_count": len(customers),
            "status": "SUCCESS",
        }

        print("=" * 40)
        print("INGESTION COMPLETED")
        print(metrics)

        return orders, customers, metrics

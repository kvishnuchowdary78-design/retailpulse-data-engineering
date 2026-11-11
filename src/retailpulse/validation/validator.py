
import pandas as pd
from datetime import datetime, timezone


class DataValidator:
    """
    Validate retail orders and customer records.
    Invalid records are preserved with rejection reasons.
    """

    REQUIRED_ORDER_COLUMNS = [
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

    REQUIRED_CUSTOMER_COLUMNS = [
        "customer_id",
        "customer_name",
        "email",
        "city",
        "registration_date",
    ]

    # Known products in our synthetic retail product catalogue.
    VALID_PRODUCTS = {
        "P001", "P002", "P003", "P004", "P005"
    }

    def validate_customers(self, customers):
        """Validate customer records and identify duplicate IDs."""

        df = customers.copy().reset_index(drop=True)

        if not set(self.REQUIRED_CUSTOMER_COLUMNS).issubset(df.columns):
            raise ValueError(
                "Customer schema is missing required columns."
            )

        df["source_record"] = range(1, len(df) + 1)

        if "source_file" not in df.columns:
            df["source_file"] = "customers.json"

        df["rejection_reason"] = ""

        required = [
            "customer_id",
            "customer_name",
            "email",
            "city",
            "registration_date",
        ]

        for column in required:
            missing = (
                df[column].isna()
                | df[column].astype("string").str.strip().eq("").fillna(True)
            )

            df.loc[missing, "rejection_reason"] += (
                f"Missing required field: {column}; "
            )

        invalid_date = pd.to_datetime(
            df["registration_date"],
            errors="coerce"
        ).isna()

        df.loc[invalid_date, "rejection_reason"] += (
            "Invalid registration_date; "
        )

        duplicate_id = (
            df["customer_id"].notna()
            & df["customer_id"].duplicated(keep="first")
        )

        df.loc[duplicate_id, "rejection_reason"] += (
            "Duplicate customer_id; "
        )

        rejected = df[
            df["rejection_reason"] != ""
        ].copy()

        accepted = df[
            df["rejection_reason"] == ""
        ].copy()

        return accepted, rejected

    def validate_orders(self, orders, valid_customer_ids):
        """Validate orders against schema and business rules."""

        df = orders.copy().reset_index(drop=True)

        missing_columns = (
            set(self.REQUIRED_ORDER_COLUMNS) - set(df.columns)
        )

        if missing_columns:
            raise ValueError(
                f"Order schema missing columns: {missing_columns}"
            )

        df["source_record"] = range(2, len(df) + 2)

        if "source_file" not in df.columns:
            df["source_file"] = "orders.csv"

        df["rejection_reason"] = ""

        # 1. Required fields
        required_fields = [
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

        for column in required_fields:
            missing = (
                df[column].isna()
                | df[column].astype("string").str.strip().eq("").fillna(True)
            )

            df.loc[missing, "rejection_reason"] += (
                f"Missing required field: {column}; "
            )

        # 2. Numeric validation
        df["line_id_numeric"] = pd.to_numeric(
            df["line_id"],
            errors="coerce"
        )

        df["quantity_numeric"] = pd.to_numeric(
            df["quantity"],
            errors="coerce"
        )

        df["unit_price_numeric"] = pd.to_numeric(
            df["unit_price"],
            errors="coerce"
        )

        invalid_line = (
            df["line_id_numeric"].isna()
            | (df["line_id_numeric"] <= 0)
        )

        df.loc[invalid_line, "rejection_reason"] += (
            "Invalid line_id; "
        )

        invalid_quantity = (
            df["quantity_numeric"].isna()
            | (df["quantity_numeric"] <= 0)
        )

        df.loc[invalid_quantity, "rejection_reason"] += (
            "Invalid quantity; "
        )

        invalid_price = (
            df["unit_price_numeric"].isna()
            | (df["unit_price_numeric"] < 0)
        )

        df.loc[invalid_price, "rejection_reason"] += (
            "Invalid unit_price; "
        )

        # 3. Timestamp validation
        df["parsed_timestamp"] = pd.to_datetime(
            df["order_timestamp"],
            errors="coerce",
            utc=True
        )

        invalid_timestamp = df["parsed_timestamp"].isna()

        df.loc[invalid_timestamp, "rejection_reason"] += (
            "Invalid order_timestamp; "
        )

        current_time = pd.Timestamp.now(tz="UTC")

        future_timestamp = (
            df["parsed_timestamp"] > current_time
        )

        df.loc[future_timestamp, "rejection_reason"] += (
            "Future order_timestamp; "
        )

        # 4. Referential integrity
        invalid_customer = (
            df["customer_id"].notna()
            & df["customer_id"].astype("string").str.strip().ne("")
            & ~df["customer_id"].isin(valid_customer_ids)
        )

        df.loc[invalid_customer, "rejection_reason"] += (
            "Unknown customer_id; "
        )

        invalid_product = (
            df["product_id"].notna()
            & ~df["product_id"].isin(self.VALID_PRODUCTS)
        )

        df.loc[invalid_product, "rejection_reason"] += (
            "Unknown product_id; "
        )

        # 5. Duplicate order-line detection
        duplicate_key = (
            df["order_id"].notna()
            & df["line_id_numeric"].notna()
            & df.duplicated(
                subset=["order_id", "line_id_numeric"],
                keep="first"
            )
        )

        df.loc[duplicate_key, "rejection_reason"] += (
            "Duplicate order line; "
        )

        # 6. Late-arrival detection
        # Invalid and future timestamps must not influence
        # the event-time watermark.
        valid_event_timestamps = df.loc[
            df["parsed_timestamp"].notna()
            & (df["parsed_timestamp"] <= current_time),
            "parsed_timestamp"
        ]

        df["is_late_arriving"] = False

        if not valid_event_timestamps.empty:
            latest_timestamp = valid_event_timestamps.max()

            late_cutoff = (
                latest_timestamp - pd.Timedelta(days=30)
            )

            df["is_late_arriving"] = (
                df["parsed_timestamp"].notna()
                & (df["parsed_timestamp"] <= current_time)
                & (df["parsed_timestamp"] < late_cutoff)
            )

        # 7. Split accepted and rejected records
        rejected = df[
            df["rejection_reason"] != ""
        ].copy()

        accepted = df[
            df["rejection_reason"] == ""
        ].copy()

        # Convert validated numeric columns into usable types.
        accepted["line_id"] = (
            accepted["line_id_numeric"].astype("int64")
        )

        accepted["quantity"] = (
            accepted["quantity_numeric"].astype("int64")
        )

        accepted["unit_price"] = (
            accepted["unit_price_numeric"]
        )

        return accepted, rejected


def save_validation_results(
    accepted_orders,
    rejected_orders,
    accepted_customers,
    rejected_customers,
    processed_dir,
    quarantine_dir
):
    """Save accepted data and rejected records separately."""

    processed_dir.mkdir(parents=True, exist_ok=True)
    quarantine_dir.mkdir(parents=True, exist_ok=True)

    accepted_orders.to_csv(
        processed_dir / "accepted_orders.csv",
        index=False
    )

    rejected_orders.to_csv(
        quarantine_dir / "rejected_orders.csv",
        index=False
    )

    accepted_customers.to_csv(
        processed_dir / "accepted_customers.csv",
        index=False
    )

    rejected_customers.to_csv(
        quarantine_dir / "rejected_customers.csv",
        index=False
    )

    print("\nVALIDATION FILES SAVED")
    print(f"Accepted orders: {processed_dir}")
    print(f"Rejected orders: {quarantine_dir}")

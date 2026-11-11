
import json
from pathlib import Path

import pandas as pd

from retailpulse.transformation.transform import transform_all


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "outputs"


def main():
    report_path = OUTPUT_DIR / "validation_report.json"

    with report_path.open("r", encoding="utf-8") as file:
        report = json.load(file)

    run_id = report["run_id"]

    orders = pd.read_csv(
        PROCESSED_DIR / "accepted_orders.csv"
    )

    customers = pd.read_csv(
        PROCESSED_DIR / "accepted_customers.csv"
    )

    results = transform_all(
        orders,
        customers,
        run_id
    )

    transformed_dir = (
        PROCESSED_DIR / "warehouse"
    )

    transformed_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    for table_name, dataframe in results.items():
        output_path = (
            transformed_dir / f"{table_name}.parquet"
        )

        dataframe.to_parquet(
            output_path,
            index=False
        )

        print(f"Saved: {output_path}")

    print("\nTRANSFORMATION SUMMARY")

    for name, dataframe in results.items():
        print(f"{name}: {len(dataframe)} rows")


if __name__ == "__main__":
    main()

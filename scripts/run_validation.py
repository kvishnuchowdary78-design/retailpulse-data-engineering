
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from retailpulse.ingestion.loader import DataLoader
from retailpulse.validation.validator import (
    DataValidator,
    save_validation_results,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
QUARANTINE_DIR = PROJECT_ROOT / "data" / "quarantine"
OUTPUT_DIR = PROJECT_ROOT / "outputs"


def main():
    run_id = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc)

    print("\nRETAILPULSE VALIDATION PIPELINE")
    print("=" * 50)
    print(f"Run ID: {run_id}")

    # Step 1: Ingest source data
    loader = DataLoader(RAW_DIR)
    orders, customers, ingestion_metrics = loader.load_all()

    # Step 2: Initialize validator
    validator = DataValidator()

    # Step 3: Validate customers first
    valid_customers, rejected_customers = (
        validator.validate_customers(customers)
    )

    valid_customer_ids = set(
        valid_customers["customer_id"].dropna()
    )

    # Step 4: Validate orders using valid customer IDs
    valid_orders, rejected_orders = (
        validator.validate_orders(
            orders,
            valid_customer_ids
        )
    )

    # Step 5: Save accepted and rejected records
    save_validation_results(
        valid_orders,
        rejected_orders,
        valid_customers,
        rejected_customers,
        PROCESSED_DIR,
        QUARANTINE_DIR,
    )

    # Step 6: Calculate metrics
    ended_at = datetime.now(timezone.utc)

    metrics = {
        "run_id": run_id,
        "status": "SUCCESS",
        "started_at": started_at.isoformat(),
        "ended_at": ended_at.isoformat(),
        "input_orders": len(orders),
        "accepted_orders": len(valid_orders),
        "rejected_orders": len(rejected_orders),
        "input_customers": len(customers),
        "accepted_customers": len(valid_customers),
        "rejected_customers": len(rejected_customers),
        "late_arriving_orders": int(
            valid_orders["is_late_arriving"].sum()
        ),
        "ingestion_status": ingestion_metrics["status"],
    }

    # Step 7: Verify reconciliation
    assert (
        metrics["input_orders"]
        == metrics["accepted_orders"]
        + metrics["rejected_orders"]
    ), "Order reconciliation failed"

    assert (
        metrics["input_customers"]
        == metrics["accepted_customers"]
        + metrics["rejected_customers"]
    ), "Customer reconciliation failed"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    report_path = OUTPUT_DIR / "validation_report.json"

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=4)

    print("\nVALIDATION SUMMARY")
    print("=" * 50)

    for key, value in metrics.items():
        print(f"{key}: {value}")

    print("=" * 50)
    print("DATA VALIDATION COMPLETED SUCCESSFULLY")
    print(f"Report saved: {report_path}")


if __name__ == "__main__":
    main()

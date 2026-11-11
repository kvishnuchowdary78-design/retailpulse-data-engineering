
from pathlib import Path

from retailpulse.ingestion.loader import DataLoader


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIRECTORY = PROJECT_ROOT / "data" / "raw"


def main():
    loader = DataLoader(RAW_DIRECTORY)

    orders, customers, metrics = loader.load_all()

    print("\nORDER DATA PREVIEW")
    print(orders.head())

    print("\nCUSTOMER DATA PREVIEW")
    print(customers.head())

    print("\nINGESTION METRICS")
    print(metrics)


if __name__ == "__main__":
    main()

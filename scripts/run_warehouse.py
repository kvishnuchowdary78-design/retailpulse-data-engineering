
from pathlib import Path
from retailpulse.warehouse.loader import WarehouseLoader


def main():
    project_root = Path(__file__).resolve().parents[1]

    print("RETAILPULSE WAREHOUSE LOAD")
    print("=" * 40)

    loader = WarehouseLoader(project_root)
    loader.load_tables()


if __name__ == "__main__":
    main()

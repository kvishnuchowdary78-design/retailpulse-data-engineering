
import pandas as pd


def transform_customers(customers):
    """Prepare the customer dimension."""

    df = customers.copy()

    df["customer_id"] = (
        df["customer_id"].astype("string").str.strip()
    )

    df["customer_name"] = (
        df["customer_name"].astype("string").str.strip()
    )

    df["city"] = (
        df["city"].astype("string").str.strip()
    )

    df["registration_date"] = pd.to_datetime(
        df["registration_date"],
        errors="raise"
    ).dt.date

    dimension = df[
        [
            "customer_id",
            "customer_name",
            "email",
            "city",
            "registration_date",
        ]
    ].drop_duplicates(subset=["customer_id"])

    return dimension.reset_index(drop=True)


def transform_products(orders):
    """Build the product dimension from valid order records."""

    df = orders.copy()

    dimension = df[
        [
            "product_id",
            "product_name",
            "category",
            "unit_price",
        ]
    ].drop_duplicates(subset=["product_id"])

    dimension = dimension.rename(
        columns={"unit_price": "observed_unit_price"}
    )

    return dimension.reset_index(drop=True)


def transform_dates(orders):
    """Create a calendar dimension."""

    df = orders.copy()

    timestamps = pd.to_datetime(
        df["order_timestamp"],
        utc=True,
        errors="raise"
    )

    dates = pd.DataFrame({
        "full_date": timestamps.dt.date
    }).drop_duplicates()

    dates["date_key"] = dates["full_date"].apply(
        lambda value: int(value.strftime("%Y%m%d"))
    )

    dates["year"] = pd.to_datetime(
        dates["full_date"]
    ).dt.year

    dates["month"] = pd.to_datetime(
        dates["full_date"]
    ).dt.month

    dates["day"] = pd.to_datetime(
        dates["full_date"]
    ).dt.day

    dates["quarter"] = (
        (dates["month"] - 1) // 3 + 1
    )

    dates["month_name"] = pd.to_datetime(
        dates["full_date"]
    ).dt.strftime("%B")

    return dates.reset_index(drop=True)


def transform_sales(
    orders,
    run_id
):
    """Prepare the sales fact table."""

    df = orders.copy()

    df["order_timestamp"] = pd.to_datetime(
        df["order_timestamp"],
        utc=True,
        errors="raise"
    )

    df["quantity"] = pd.to_numeric(
        df["quantity"],
        errors="raise"
    ).astype("int64")

    df["unit_price"] = pd.to_numeric(
        df["unit_price"],
        errors="raise"
    ).round(2)

    df["revenue"] = (
        df["quantity"] * df["unit_price"]
    ).round(2)

    df["date_key"] = df[
        "order_timestamp"
    ].dt.strftime("%Y%m%d").astype("int64")

    df["run_id"] = run_id

    columns = [
        "order_id",
        "line_id",
        "customer_id",
        "product_id",
        "date_key",
        "order_timestamp",
        "quantity",
        "unit_price",
        "revenue",
        "is_late_arriving",
        "run_id",
        "source_file",
        "source_record",
    ]

    return df[columns].reset_index(drop=True)


def transform_all(
    orders,
    customers,
    run_id
):
    """Execute all transformations."""

    print("\nRETAILPULSE TRANSFORMATION")
    print("=" * 45)

    customer_dimension = transform_customers(customers)

    product_dimension = transform_products(orders)

    date_dimension = transform_dates(orders)

    sales_fact = transform_sales(orders, run_id)

    print(
        f"Customer dimension: {len(customer_dimension)} rows"
    )

    print(
        f"Product dimension: {len(product_dimension)} rows"
    )

    print(
        f"Date dimension: {len(date_dimension)} rows"
    )

    print(
        f"Sales fact: {len(sales_fact)} rows"
    )

    print("=" * 45)
    print("TRANSFORMATION COMPLETED")

    return {
        "dim_customer": customer_dimension,
        "dim_product": product_dimension,
        "dim_date": date_dimension,
        "fact_sales": sales_fact,
    }

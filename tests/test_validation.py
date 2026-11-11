
import pandas as pd
import pytest

from retailpulse.validation.validator import DataValidator


# --------------------------------------------------
# FIXTURES
# --------------------------------------------------

@pytest.fixture
def validator():
    return DataValidator()


@pytest.fixture
def valid_customer_ids():
    return {"C001", "C002"}


# --------------------------------------------------
# SAMPLE DATA GENERATORS
# --------------------------------------------------

def make_order(**overrides):
    order = {
        "order_id": "O1001",
        "line_id": 1,
        "customer_id": "C001",
        "product_id": "P001",
        "product_name": "Laptop",
        "category": "Electronics",
        "order_timestamp": "2026-11-01T10:30:00Z",
        "quantity": 1,
        "unit_price": 55000,
    }

    order.update(overrides)
    return order


def make_customer(**overrides):
    customer = {
        "customer_id": "C001",
        "customer_name": "Customer One",
        "email": "customer1@example.com",
        "city": "Bengaluru",
        "registration_date": "2025-01-15",
    }

    customer.update(overrides)
    return customer


# --------------------------------------------------
# ORDER VALIDATION TESTS
# --------------------------------------------------

def test_valid_order_is_accepted(validator, valid_customer_ids):
    accepted, rejected = validator.validate_orders(
        pd.DataFrame([make_order()]),
        valid_customer_ids
    )

    assert len(accepted) == 1
    assert len(rejected) == 0
    assert accepted.iloc[0]["quantity"] == 1


def test_missing_order_field_is_rejected(validator, valid_customer_ids):
    accepted, rejected = validator.validate_orders(
        pd.DataFrame([
            make_order(customer_id=None)
        ]),
        valid_customer_ids
    )

    assert len(accepted) == 0
    assert len(rejected) == 1

    assert "Missing required field: customer_id" in (
        rejected.iloc[0]["rejection_reason"]
    )


def test_negative_quantity_is_rejected(validator, valid_customer_ids):
    accepted, rejected = validator.validate_orders(
        pd.DataFrame([
            make_order(quantity=-2)
        ]),
        valid_customer_ids
    )

    assert len(accepted) == 0
    assert len(rejected) == 1

    assert "Invalid quantity" in (
        rejected.iloc[0]["rejection_reason"]
    )


def test_zero_price_is_accepted(validator, valid_customer_ids):
    accepted, rejected = validator.validate_orders(
        pd.DataFrame([
            make_order(unit_price=0)
        ]),
        valid_customer_ids
    )

    assert len(accepted) == 1
    assert len(rejected) == 0


def test_unknown_customer_is_rejected(validator, valid_customer_ids):
    accepted, rejected = validator.validate_orders(
        pd.DataFrame([
            make_order(customer_id="C999")
        ]),
        valid_customer_ids
    )

    assert len(accepted) == 0

    assert "Unknown customer_id" in (
        rejected.iloc[0]["rejection_reason"]
    )


def test_unknown_product_is_rejected(validator, valid_customer_ids):
    accepted, rejected = validator.validate_orders(
        pd.DataFrame([
            make_order(product_id="P999")
        ]),
        valid_customer_ids
    )

    assert len(accepted) == 0

    assert "Unknown product_id" in (
        rejected.iloc[0]["rejection_reason"]
    )


def test_duplicate_order_line_is_rejected(validator, valid_customer_ids):
    orders = pd.DataFrame([
        make_order(),
        make_order()
    ])

    accepted, rejected = validator.validate_orders(
        orders,
        valid_customer_ids
    )

    assert len(accepted) == 1
    assert len(rejected) == 1

    assert "Duplicate order line" in (
        rejected.iloc[0]["rejection_reason"]
    )


def test_invalid_timestamp_is_rejected(validator, valid_customer_ids):
    accepted, rejected = validator.validate_orders(
        pd.DataFrame([
            make_order(order_timestamp="not-a-date")
        ]),
        valid_customer_ids
    )

    assert len(accepted) == 0

    assert "Invalid order_timestamp" in (
        rejected.iloc[0]["rejection_reason"]
    )


def test_late_order_is_accepted_and_flagged(
    validator,
    valid_customer_ids
):
    orders = pd.DataFrame([
        make_order(
            order_id="O2001",
            order_timestamp="2026-01-01T10:00:00Z"
        ),
        make_order(
            order_id="O2002",
            order_timestamp="2026-03-15T10:00:00Z"
        )
    ])

    accepted, rejected = validator.validate_orders(
        orders,
        valid_customer_ids
    )

    assert len(accepted) == 2
    assert len(rejected) == 0

    late_order = accepted[
        accepted["order_id"] == "O2001"
    ].iloc[0]

    assert late_order["is_late_arriving"] == True


def test_future_order_is_rejected(validator, valid_customer_ids):
    accepted, rejected = validator.validate_orders(
        pd.DataFrame([
            make_order(
                order_timestamp="2099-01-01T10:00:00Z"
            )
        ]),
        valid_customer_ids
    )

    assert len(accepted) == 0
    assert len(rejected) == 1

    assert "Future order_timestamp" in (
        rejected.iloc[0]["rejection_reason"]
    )


# --------------------------------------------------
# CUSTOMER VALIDATION TESTS
# --------------------------------------------------

def test_valid_customer_is_accepted(validator):
    accepted, rejected = validator.validate_customers(
        pd.DataFrame([
            make_customer()
        ])
    )

    assert len(accepted) == 1
    assert len(rejected) == 0


def test_duplicate_customer_is_rejected(validator):
    customers = pd.DataFrame([
        make_customer(),
        make_customer()
    ])

    accepted, rejected = validator.validate_customers(
        customers
    )

    assert len(accepted) == 1
    assert len(rejected) == 1

    assert "Duplicate customer_id" in (
        rejected.iloc[0]["rejection_reason"]
    )


def test_missing_customer_name_is_rejected(validator):
    accepted, rejected = validator.validate_customers(
        pd.DataFrame([
            make_customer(customer_name="")
        ])
    )

    assert len(accepted) == 0
    assert len(rejected) == 1

    assert "Missing required field: customer_name" in (
        rejected.iloc[0]["rejection_reason"]
    )


# --------------------------------------------------
# SCHEMA AND EMPTY INPUT TESTS
# --------------------------------------------------

def test_missing_order_schema_raises_error(
    validator,
    valid_customer_ids
):
    orders = pd.DataFrame([{
        "order_id": "O1001",
        "customer_id": "C001"
    }])

    with pytest.raises(ValueError):
        validator.validate_orders(
            orders,
            valid_customer_ids
        )


def test_empty_orders_are_handled(validator, valid_customer_ids):
    empty_orders = pd.DataFrame(
        columns=DataValidator.REQUIRED_ORDER_COLUMNS
    )

    accepted, rejected = validator.validate_orders(
        empty_orders,
        valid_customer_ids
    )

    assert len(accepted) == 0
    assert len(rejected) == 0

import pandas as pd
import pytest

from src.data import generate_demo_data
from src.validation import DataValidationError, validate_inventory, validate_transactions


def test_duplicate_order_id_is_rejected() -> None:
    transactions, _ = generate_demo_data()
    transactions.loc[1, "order_id"] = transactions.loc[0, "order_id"]

    with pytest.raises(DataValidationError, match="duplicates"):
        validate_transactions(transactions)


@pytest.mark.parametrize(
    ("column", "value", "message"),
    [
        ("shipped_units", 10_000, "shipped_units"),
        ("defective_units", 10_000, "defective_units"),
        ("freight_cost_mxn", -1, "non-negative"),
    ],
)
def test_invalid_quantity_is_rejected(column: str, value: int, message: str) -> None:
    transactions, _ = generate_demo_data()
    transactions.loc[0, column] = value

    with pytest.raises(DataValidationError, match=message):
        validate_transactions(transactions)


def test_nonpositive_inventory_is_rejected() -> None:
    _, inventory = generate_demo_data()
    inventory.loc[0, "end_inventory_mxn"] = 0

    with pytest.raises(DataValidationError, match="positive"):
        validate_inventory(inventory)


def test_missing_required_value_is_rejected() -> None:
    transactions, _ = generate_demo_data()
    transactions.loc[0, "supplier"] = pd.NA

    with pytest.raises(DataValidationError, match="nulls"):
        validate_transactions(transactions)


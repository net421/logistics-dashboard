import pandas as pd

from src.data import generate_demo_data
from src.validation import validate_inventory, validate_transactions


def test_demo_data_is_deterministic_and_valid() -> None:
    first_transactions, first_inventory = generate_demo_data(seed=42)
    second_transactions, second_inventory = generate_demo_data(seed=42)

    pd.testing.assert_frame_equal(first_transactions, second_transactions)
    pd.testing.assert_frame_equal(first_inventory, second_inventory)
    validate_transactions(first_transactions)
    validate_inventory(first_inventory)


def test_different_seed_changes_scenario_without_changing_schema() -> None:
    first_transactions, first_inventory = generate_demo_data(seed=42)
    second_transactions, second_inventory = generate_demo_data(seed=7)

    assert list(first_transactions.columns) == list(second_transactions.columns)
    assert list(first_inventory.columns) == list(second_inventory.columns)
    assert not first_transactions.equals(second_transactions)


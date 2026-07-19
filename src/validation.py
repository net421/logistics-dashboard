"""Data-contract checks for dashboard inputs."""

from __future__ import annotations

import pandas as pd


class DataValidationError(ValueError):
    """Raised when an input frame violates the dashboard data contract."""


TRANSACTION_COLUMNS = {
    "order_id",
    "order_date",
    "promised_date",
    "delivery_date",
    "supplier",
    "route",
    "ordered_units",
    "shipped_units",
    "defective_units",
    "freight_cost_mxn",
}

INVENTORY_COLUMNS = {
    "month",
    "cogs_mxn",
    "begin_inventory_mxn",
    "end_inventory_mxn",
}


def _missing_columns(frame: pd.DataFrame, required: set[str]) -> list[str]:
    return sorted(required.difference(frame.columns))


def validate_transactions(transactions: pd.DataFrame) -> None:
    """Validate keys, dates, quantities, and basic order invariants."""
    problems: list[str] = []
    missing = _missing_columns(transactions, TRANSACTION_COLUMNS)
    if missing:
        raise DataValidationError(f"Missing transaction columns: {', '.join(missing)}")
    if transactions.empty:
        problems.append("transactions must contain at least one row")
    if transactions["order_id"].isna().any():
        problems.append("order_id contains null values")
    if transactions["order_id"].duplicated().any():
        problems.append("order_id contains duplicates")

    required_values = TRANSACTION_COLUMNS.difference({"order_id"})
    if transactions[list(required_values)].isna().any().any():
        problems.append("required transaction values contain nulls")

    quantity_columns = [
        "ordered_units",
        "shipped_units",
        "defective_units",
        "freight_cost_mxn",
    ]
    if (transactions[quantity_columns] < 0).any().any():
        problems.append("quantities and freight cost must be non-negative")
    if (transactions["shipped_units"] > transactions["ordered_units"]).any():
        problems.append("shipped_units cannot exceed ordered_units")
    if (transactions["defective_units"] > transactions["shipped_units"]).any():
        problems.append("defective_units cannot exceed shipped_units")
    if (transactions["promised_date"] < transactions["order_date"]).any():
        problems.append("promised_date cannot precede order_date")
    if (transactions["delivery_date"] < transactions["order_date"]).any():
        problems.append("delivery_date cannot precede order_date")

    if problems:
        raise DataValidationError("; ".join(problems))


def validate_inventory(inventory: pd.DataFrame) -> None:
    """Validate the monthly inventory inputs used for turnover."""
    problems: list[str] = []
    missing = _missing_columns(inventory, INVENTORY_COLUMNS)
    if missing:
        raise DataValidationError(f"Missing inventory columns: {', '.join(missing)}")
    if inventory.empty:
        problems.append("inventory must contain at least one row")
    if inventory["month"].isna().any():
        problems.append("inventory month contains null values")
    if inventory["month"].duplicated().any():
        problems.append("inventory month contains duplicates")
    value_columns = ["cogs_mxn", "begin_inventory_mxn", "end_inventory_mxn"]
    if inventory[value_columns].isna().any().any():
        problems.append("inventory values contain nulls")
    if (inventory[value_columns] <= 0).any().any():
        problems.append("inventory values must be positive")
    if problems:
        raise DataValidationError("; ".join(problems))


def quality_summary(transactions: pd.DataFrame) -> dict[str, int]:
    """Return simple audit counts displayed in the app."""
    return {
        "rows": len(transactions),
        "duplicate_order_ids": int(transactions["order_id"].duplicated().sum()),
        "missing_required_values": int(transactions.isna().sum().sum()),
        "invalid_quantities": int(
            (transactions["shipped_units"] > transactions["ordered_units"]).sum()
            + (transactions["defective_units"] > transactions["shipped_units"]).sum()
        ),
    }


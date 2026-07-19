"""Stable order-level exports for the filtered dashboard cohort."""

from __future__ import annotations

import pandas as pd


ORDER_EXPORT_COLUMNS = (
    "order_id",
    "order_date",
    "promised_date",
    "delivery_date",
    "supplier",
    "route",
    "ordered_units",
    "shipped_units",
    "unfilled_units",
    "defective_units",
    "on_time",
    "lead_time_days",
    "freight_cost_mxn",
    "freight_cost_per_shipped_unit_mxn",
)

DATE_COLUMNS = ("order_date", "promised_date", "delivery_date")


def prepare_order_export(transactions: pd.DataFrame) -> pd.DataFrame:
    """Return one auditable export row for each supplied order row.

    The caller owns cohort filtering. This function adds only derived fields
    that can be reconciled to the KPI definitions shown in the dashboard.
    """
    orders = transactions.copy()
    orders["unfilled_units"] = orders["ordered_units"] - orders["shipped_units"]
    orders["on_time"] = orders["delivery_date"] <= orders["promised_date"]
    orders["lead_time_days"] = (
        orders["delivery_date"] - orders["order_date"]
    ).dt.days
    shipped_units = orders["shipped_units"].replace(0, float("nan"))
    orders["freight_cost_per_shipped_unit_mxn"] = (
        orders["freight_cost_mxn"].div(shipped_units).round(2)
    )
    return (
        orders.loc[:, list(ORDER_EXPORT_COLUMNS)]
        .sort_values(["order_date", "order_id"], kind="stable")
        .reset_index(drop=True)
    )


def serialize_order_export(orders: pd.DataFrame) -> bytes:
    """Serialize a prepared export as deterministic, Excel-friendly CSV bytes."""
    export = orders.loc[:, list(ORDER_EXPORT_COLUMNS)].copy()
    for column in DATE_COLUMNS:
        export[column] = export[column].dt.strftime("%Y-%m-%d")
    csv_text = export.to_csv(
        index=False,
        lineterminator="\n",
        float_format="%.2f",
        na_rep="",
    )
    return csv_text.encode("utf-8-sig")

"""Auditable KPI calculations for the logistics dashboard."""

from __future__ import annotations

import numpy as np
import pandas as pd


def filter_period(
    transactions: pd.DataFrame,
    inventory: pd.DataFrame,
    start_month: str,
    end_month: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Filter both fact sets to an inclusive YYYY-MM period."""
    start = pd.Period(start_month, freq="M")
    end = pd.Period(end_month, freq="M")
    if start > end:
        raise ValueError("start_month must be before or equal to end_month")

    order_month = transactions["order_date"].dt.to_period("M")
    inventory_month = inventory["month"].dt.to_period("M")
    order_mask = order_month.between(start, end)
    inventory_mask = inventory_month.between(start, end)
    return (
        transactions.loc[order_mask].copy(),
        inventory.loc[inventory_mask].copy(),
    )


def monthly_kpis(
    transactions: pd.DataFrame, inventory: pd.DataFrame
) -> pd.DataFrame:
    """Aggregate order rows into monthly operational KPIs."""
    facts = transactions.copy()
    facts["month"] = facts["order_date"].dt.to_period("M").dt.to_timestamp()
    facts["on_time"] = facts["delivery_date"] <= facts["promised_date"]
    facts["lead_time_days"] = (
        facts["delivery_date"] - facts["order_date"]
    ).dt.days

    grouped = facts.groupby("month", as_index=False).agg(
        orders=("order_id", "nunique"),
        on_time_orders=("on_time", "sum"),
        ordered_units=("ordered_units", "sum"),
        shipped_units=("shipped_units", "sum"),
        freight_cost_mxn=("freight_cost_mxn", "sum"),
        lead_time_days=("lead_time_days", "mean"),
    )
    grouped["otd"] = grouped["on_time_orders"] / grouped["orders"] * 100
    grouped["fulfillment"] = (
        grouped["shipped_units"] / grouped["ordered_units"] * 100
    )
    grouped["freight"] = (
        grouped["freight_cost_mxn"] / grouped["shipped_units"]
    )

    stock = inventory.copy()
    stock["month"] = stock["month"].dt.to_period("M").dt.to_timestamp()
    average_inventory = (
        stock["begin_inventory_mxn"] + stock["end_inventory_mxn"]
    ) / 2
    stock["turnover"] = 12 * stock["cogs_mxn"] / average_inventory

    result = grouped.merge(stock[["month", "turnover"]], on="month", how="left")
    result["month_label"] = result["month"].dt.strftime("%b %Y")
    numeric = ["otd", "fulfillment", "freight", "lead_time_days", "turnover"]
    result[numeric] = result[numeric].round(2)
    return result.sort_values("month").reset_index(drop=True)


def supplier_scorecard(transactions: pd.DataFrame) -> pd.DataFrame:
    """Aggregate supplier service, quality, and volume from filtered orders."""
    facts = transactions.assign(
        on_time=transactions["delivery_date"] <= transactions["promised_date"],
        lead_time_days=(
            transactions["delivery_date"] - transactions["order_date"]
        ).dt.days,
    )
    result = facts.groupby("supplier", as_index=False).agg(
        orders=("order_id", "nunique"),
        on_time_orders=("on_time", "sum"),
        shipped_units=("shipped_units", "sum"),
        defective_units=("defective_units", "sum"),
        lead_time=("lead_time_days", "mean"),
    )
    result["otd"] = result["on_time_orders"] / result["orders"] * 100
    result["defect_rate"] = (
        result["defective_units"] / result["shipped_units"] * 100
    )
    result[["otd", "defect_rate", "lead_time"]] = result[
        ["otd", "defect_rate", "lead_time"]
    ].round(2)
    return result.sort_values(["otd", "defect_rate"], ascending=[False, True])


def route_scorecard(transactions: pd.DataFrame) -> pd.DataFrame:
    """Aggregate service, unit cost, and volume for each route."""
    facts = transactions.assign(
        on_time=transactions["delivery_date"] <= transactions["promised_date"],
        lead_time_days=(
            transactions["delivery_date"] - transactions["order_date"]
        ).dt.days,
    )
    result = facts.groupby("route", as_index=False).agg(
        orders=("order_id", "nunique"),
        on_time_orders=("on_time", "sum"),
        volume=("shipped_units", "sum"),
        freight_cost_mxn=("freight_cost_mxn", "sum"),
        avg_days=("lead_time_days", "mean"),
    )
    result["otd"] = result["on_time_orders"] / result["orders"] * 100
    result["cost_unit"] = result["freight_cost_mxn"] / result["volume"]
    result[["otd", "cost_unit", "avg_days"]] = result[
        ["otd", "cost_unit", "avg_days"]
    ].round(2)
    return result.sort_values("volume", ascending=False)


def safe_delta(current: float, previous: float) -> float:
    """Return a finite absolute delta for a KPI card."""
    delta = float(current) - float(previous)
    return delta if np.isfinite(delta) else 0.0

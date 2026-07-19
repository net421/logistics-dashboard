"""Deterministic synthetic operating data used by the demo dashboard.

The generated rows model individual orders.  Dashboard KPIs are deliberately
calculated downstream from these rows rather than generated as finished
percentages.  This keeps the demo reproducible and makes each metric auditable.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Route:
    name: str
    transit_days: int
    freight_mxn_per_unit: float


SUPPLIERS = (
    "Proveedor Alpha",
    "Proveedor Beta",
    "Proveedor Gamma",
    "Proveedor Delta",
    "Proveedor Epsilon",
)

ROUTES = (
    Route("CDMX → Monterrey", 3, 18.0),
    Route("CDMX → Guadalajara", 2, 14.0),
    Route("Puebla → Veracruz", 2, 12.0),
    Route("Monterrey → Tijuana", 4, 27.0),
    Route("Guadalajara → Cancún", 4, 24.0),
)


def generate_demo_data(seed: int = 42) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return order-level and inventory data for a reproducible 12-month scenario."""
    rng = np.random.default_rng(seed)
    month_starts = pd.date_range("2025-01-01", periods=12, freq="MS")
    orders: list[dict[str, object]] = []

    for month_index, month_start in enumerate(month_starts):
        order_count = 72 + month_index * 2
        on_time_probability = min(0.84 + month_index * 0.011, 0.97)
        full_ship_probability = min(0.86 + month_index * 0.009, 0.97)

        for order_number in range(order_count):
            route_index = int(rng.integers(0, len(ROUTES)))
            route = ROUTES[route_index]
            supplier_index = int(rng.integers(0, len(SUPPLIERS)))
            supplier = SUPPLIERS[supplier_index]
            day_offset = int(rng.integers(0, month_start.days_in_month))
            order_date = month_start + timedelta(days=day_offset)

            ordered_units = int(rng.integers(30, 260))
            if rng.random() <= full_ship_probability:
                shipped_units = ordered_units
            else:
                shortage = int(rng.integers(1, max(2, ordered_units // 6)))
                shipped_units = ordered_units - shortage

            promised_days = route.transit_days + 2
            promised_date = order_date + timedelta(days=promised_days)
            if rng.random() <= on_time_probability:
                actual_days = max(1, promised_days - int(rng.integers(0, 3)))
            else:
                actual_days = promised_days + int(rng.integers(1, 5))
            delivery_date = order_date + timedelta(days=actual_days)

            supplier_risk = 0.004 + supplier_index * 0.003
            defective_units = int(rng.binomial(shipped_units, supplier_risk))
            freight_rate = route.freight_mxn_per_unit * rng.normal(1.0, 0.06)
            freight_cost_mxn = round(shipped_units * freight_rate, 2)

            orders.append(
                {
                    "order_id": f"ORD-{month_start:%Y%m}-{order_number + 1:04d}",
                    "order_date": order_date,
                    "promised_date": promised_date,
                    "delivery_date": delivery_date,
                    "supplier": supplier,
                    "route": route.name,
                    "ordered_units": ordered_units,
                    "shipped_units": shipped_units,
                    "defective_units": defective_units,
                    "freight_cost_mxn": freight_cost_mxn,
                }
            )

    transactions = pd.DataFrame(orders)
    inventory_rows: list[dict[str, object]] = []
    opening_inventory = 1_250_000.0
    for month_index, month_start in enumerate(month_starts):
        monthly_units = transactions.loc[
            transactions["order_date"].dt.to_period("M") == month_start.to_period("M"),
            "shipped_units",
        ].sum()
        cogs_mxn = round(monthly_units * rng.normal(135.0, 4.0), 2)
        ending_inventory = round(
            max(750_000.0, opening_inventory + rng.normal(-16_000, 42_000)), 2
        )
        inventory_rows.append(
            {
                "month": month_start,
                "cogs_mxn": cogs_mxn,
                "begin_inventory_mxn": round(opening_inventory, 2),
                "end_inventory_mxn": ending_inventory,
            }
        )
        opening_inventory = ending_inventory

    inventory = pd.DataFrame(inventory_rows)
    return transactions, inventory

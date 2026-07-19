from io import BytesIO

import pandas as pd

from src.export import (
    ORDER_EXPORT_COLUMNS,
    prepare_order_export,
    serialize_order_export,
)
from src.kpis import filter_period, route_scorecard


def _transactions() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": ["FEB-2", "JAN-1", "FEB-1"],
            "order_date": pd.to_datetime(
                ["2025-02-12", "2025-01-03", "2025-02-01"]
            ),
            "promised_date": pd.to_datetime(
                ["2025-02-17", "2025-01-08", "2025-02-06"]
            ),
            "delivery_date": pd.to_datetime(
                ["2025-02-18", "2025-01-07", "2025-02-05"]
            ),
            "supplier": ["Beta", "Alpha", "Alpha"],
            "route": ["North", "South", "North"],
            "ordered_units": [100, 80, 50],
            "shipped_units": [90, 80, 50],
            "defective_units": [2, 0, 1],
            "freight_cost_mxn": [945.0, 800.0, 550.0],
        }
    )


def _inventory() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "month": pd.to_datetime(["2025-01-01", "2025-02-01"]),
            "cogs_mxn": [1_000.0, 1_200.0],
            "begin_inventory_mxn": [2_000.0, 2_000.0],
            "end_inventory_mxn": [2_000.0, 2_000.0],
        }
    )


def test_export_uses_exactly_the_filtered_order_cohort() -> None:
    filtered, _ = filter_period(
        _transactions(), _inventory(), "2025-02", "2025-02"
    )

    export = prepare_order_export(filtered)

    assert export["order_id"].tolist() == ["FEB-1", "FEB-2"]
    assert len(export) == filtered["order_id"].nunique()
    assert set(export["order_id"]) == set(filtered["order_id"])


def test_export_has_one_row_per_order_and_auditable_derived_columns() -> None:
    export = prepare_order_export(_transactions())

    assert tuple(export.columns) == ORDER_EXPORT_COLUMNS
    assert export["order_id"].is_unique
    feb_2 = export.set_index("order_id").loc["FEB-2"]
    assert feb_2["unfilled_units"] == 10
    assert not bool(feb_2["on_time"])
    assert feb_2["lead_time_days"] == 6
    assert feb_2["freight_cost_per_shipped_unit_mxn"] == 10.5


def test_csv_serialization_is_stable_and_round_trips() -> None:
    export = prepare_order_export(_transactions())

    first = serialize_order_export(export)
    second = serialize_order_export(export)
    restored = pd.read_csv(BytesIO(first))

    assert first == second
    assert first.startswith(b"\xef\xbb\xbf")
    assert b"\r\n" not in first
    assert restored.columns.tolist() == list(ORDER_EXPORT_COLUMNS)
    assert restored["order_id"].tolist() == export["order_id"].tolist()
    assert restored["order_date"].tolist() == [
        "2025-01-03",
        "2025-02-01",
        "2025-02-12",
    ]


def test_route_unit_cost_reconciles_as_weighted_aggregate() -> None:
    transactions = _transactions()
    export = prepare_order_export(transactions)
    north_export = export.loc[export["route"] == "North"]
    north_route = route_scorecard(transactions).set_index("route").loc["North"]

    weighted_cost = (
        north_export["freight_cost_mxn"].sum()
        / north_export["shipped_units"].sum()
    )
    unweighted_mean = north_export[
        "freight_cost_per_shipped_unit_mxn"
    ].mean()

    assert north_route["cost_unit"] == round(weighted_cost, 2) == 10.68
    assert round(unweighted_mean, 2) == 10.75
    assert north_route["cost_unit"] != round(unweighted_mean, 2)

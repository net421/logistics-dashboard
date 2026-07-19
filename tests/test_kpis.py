import pandas as pd
import pytest

from src.kpis import (
    filter_period,
    monthly_kpis,
    route_scorecard,
    supplier_scorecard,
)


@pytest.fixture
def known_transactions() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": ["A", "B", "C"],
            "order_date": pd.to_datetime(["2025-01-01", "2025-01-02", "2025-02-01"]),
            "promised_date": pd.to_datetime(
                ["2025-01-06", "2025-01-07", "2025-02-06"]
            ),
            "delivery_date": pd.to_datetime(
                ["2025-01-05", "2025-01-10", "2025-02-05"]
            ),
            "supplier": ["Alpha", "Beta", "Alpha"],
            "route": ["North", "North", "South"],
            "ordered_units": [100, 100, 50],
            "shipped_units": [100, 80, 50],
            "defective_units": [1, 4, 0],
            "freight_cost_mxn": [1_000.0, 800.0, 750.0],
        }
    )


@pytest.fixture
def known_inventory() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "month": pd.to_datetime(["2025-01-01", "2025-02-01"]),
            "cogs_mxn": [1_000.0, 2_000.0],
            "begin_inventory_mxn": [2_000.0, 2_000.0],
            "end_inventory_mxn": [2_000.0, 2_000.0],
        }
    )


def test_monthly_kpis_match_manual_calculation(
    known_transactions: pd.DataFrame, known_inventory: pd.DataFrame
) -> None:
    january = monthly_kpis(known_transactions, known_inventory).iloc[0]

    assert january["orders"] == 2
    assert january["otd"] == pytest.approx(50.0)
    assert january["fulfillment"] == pytest.approx(90.0)
    assert january["freight"] == pytest.approx(10.0)
    assert january["lead_time_days"] == pytest.approx(6.0)
    assert january["turnover"] == pytest.approx(6.0)


def test_period_filter_is_inclusive_and_shared_by_all_views(
    known_transactions: pd.DataFrame, known_inventory: pd.DataFrame
) -> None:
    transactions, inventory = filter_period(
        known_transactions, known_inventory, "2025-02", "2025-02"
    )

    assert transactions["order_id"].tolist() == ["C"]
    assert inventory["month"].dt.strftime("%Y-%m").tolist() == ["2025-02"]
    assert supplier_scorecard(transactions)["orders"].sum() == 1
    assert route_scorecard(transactions)["volume"].sum() == 50


def test_invalid_period_is_rejected(
    known_transactions: pd.DataFrame, known_inventory: pd.DataFrame
) -> None:
    with pytest.raises(ValueError, match="start_month"):
        filter_period(known_transactions, known_inventory, "2025-02", "2025-01")


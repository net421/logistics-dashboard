from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_dashboard_starts_without_exception() -> None:
    dashboard_path = Path(__file__).parents[1] / "dashboard.py"
    app = AppTest.from_file(str(dashboard_path), default_timeout=30).run()

    assert not app.exception
    assert app.title[0].value == "Logistics KPI Dashboard"
    assert "sintéticos" in app.info[0].value


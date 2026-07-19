from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_dashboard_starts_without_exception() -> None:
    dashboard_path = Path(__file__).parents[1] / "dashboard.py"
    app = AppTest.from_file(str(dashboard_path), default_timeout=30).run()

    assert not app.exception
    assert app.title[0].value == "Logistics KPI Dashboard"
    assert "sintéticos" in app.info[0].value
    assert len(app.get("download_button")) == 1
    assert "órdenes filtradas" in app.get("download_button")[0].label

    app.sidebar.select_slider[0].set_value(("2025-02", "2025-02")).run()

    assert not app.exception
    assert app.get("download_button")[0].label == (
        "Descargar 74 órdenes filtradas (CSV)"
    )

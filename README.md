# Logistics KPI Dashboard

Interactive supply-chain analytics demo built with Python, pandas, Streamlit,
and Plotly. It turns reproducible **synthetic order rows** into auditable monthly,
supplier, and route KPIs.

> This is a portfolio simulation, not a production system, company dataset,
> real-time feed, SAP integration, or record of customer impact.

## What the project demonstrates

- Calculation of operational KPIs from order-level dates, quantities, costs,
  suppliers, and routes.
- One period filter applied consistently to monthly, supplier, and route views.
- Data-contract validation for duplicate keys, missing values, impossible dates,
  negative values, over-shipments, and invalid defect quantities.
- Reproducible business scenarios selected with a random seed.
- Unit tests for known KPI results plus a Streamlit application smoke test.
- Automated linting and tests in GitHub Actions.

## Dashboard

The application shows five calculated KPIs, service and cost trends, supplier
performance, a route cost–service matrix, and two automatically generated
operational observations.

![Logistics KPI Dashboard showing five KPIs and monthly service trends](docs/logistics-dashboard.png)

## KPI definitions

| KPI | Formula used in this demo | Unit |
|---|---|---|
| On-Time Delivery | Orders delivered on/before promised date ÷ delivered orders | % |
| Unit fill rate | Shipped units ÷ ordered units | % |
| Freight cost per unit | Total freight cost ÷ shipped units | MXN/unit |
| Lead time | Average of delivery date − order date | Days |
| Annualized inventory turnover | 12 × monthly COGS ÷ average monthly inventory | Times/year |

The 95% service targets are scenario references, not universal industry
standards. The bundled data intentionally contains late and partially fulfilled
orders so the dashboard has exceptions to analyze.

The period selector assigns each order to a month using `order_date`. OTD then
evaluates the completed delivery outcome for that order cohort; it is not grouped
by delivery month.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt -r requirements-dev.txt
streamlit run dashboard.py
```

Open `http://localhost:8501`, change the period or scenario seed, and verify that
all views recalculate from the same selected order rows.

## Verify

```bash
python -m ruff check .
python -m pytest -q -W error
```

The tests include a hand-calculated fixture: two January orders must produce 50%
OTD, 90% unit fill rate, MX$10 freight per shipped unit, six-day lead time, and
6x annualized inventory turnover.

## Project structure

```text
.
├── dashboard.py                 # Streamlit presentation
├── src/
│   ├── data.py                  # Deterministic order and inventory generation
│   ├── kpis.py                  # Period filtering and KPI aggregation
│   └── validation.py            # Input data contracts
├── tests/                       # Unit, validation, and AppTest smoke tests
├── docs/logistics-dashboard.png # Verified dashboard screenshot
├── .github/workflows/ci.yml     # Lint and test workflow
├── .streamlit/config.toml       # Stable local/deployed theme
├── requirements.txt
└── requirements-dev.txt
```

## Suggested interview walkthrough

1. Explain the difference between OTD and unit fill rate using their denominators.
2. Change the analysis period and show that supplier and route totals change with
   the monthly results.
3. Open `tests/test_kpis.py` and defend the expected values without running the
   dashboard.
4. Identify the lowest-OTD supplier and highest-cost route, then state which data
   would be needed before making a real operational decision.

## Limitations

- Synthetic, locally generated inputs only; no external database or scheduled
  refresh.
- All deliveries are completed; backorders are represented through partially
  shipped quantities rather than open-order lifecycle events.
- Currency and operating rules are fixed for this Mexican demo scenario.
- Results demonstrate reproducible analysis and application behavior, not
  professional production experience.

## Author

Emmanuel Beristain Guzmán · Logistics Engineer · Supply Chain Analytics<br>
[github.com/net421](https://github.com/net421)

# 📊 Logistics Dashboard — Supply Chain KPIs

> **Supply Chain Analytics Project** | Python · Streamlit · Plotly  
> Part of a logistics optimization portfolio by [Emmanuel Beristain Guzmán](https://github.com/net421)

---

## Overview

An interactive web dashboard for monitoring supply chain operations in real time. Built to demonstrate applied knowledge of logistics KPIs, data visualization, and operational analytics — skills directly relevant to **SAP MM/SD**, **supply chain consulting**, and **logistics analytics** roles.

The dashboard simulates 12 months of realistic logistics data across five key performance indicators, with filters, supplier scorecards, and route efficiency analysis.

---

## Live KPIs Monitored

| KPI | Description | Target |
|---|---|---|
| **OTD** | On-Time Delivery rate | ≥ 95% |
| **Inventory Turnover** | How many times stock cycles per year | ≥ 8x |
| **Freight Cost/Unit** | Average shipping cost per unit dispatched | Minimize |
| **Fulfillment Rate** | Orders completed without backorder | ≥ 95% |
| **Lead Time** | Average supplier delivery time (days) | Minimize |

---

## Features

- ✅ Interactive KPI cards with month-over-month delta
- ✅ Trend charts for OTD, fulfillment, freight cost, lead time
- ✅ Monthly order volume visualization
- ✅ Supplier performance scorecard (color-coded)
- ✅ Route efficiency scatter map (cost vs. transit days vs. volume)
- ✅ Sidebar filters by period and data seed
- ✅ Fully responsive — works on desktop and tablet

---

## Screenshot

> *Dashboard running locally — dark industrial aesthetic*

![Dashboard screenshot](screenshot.png)

---

## Project Structure

```
logistics-dashboard/
│
├── dashboard.py        # Main Streamlit app — all logic + UI
├── requirements.txt    # Python dependencies
├── README.md
└── screenshot.png      # Dashboard preview (for GitHub)
```

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/net421/logistics-dashboard.git
cd logistics-dashboard
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the dashboard

```bash
streamlit run dashboard.py
```

The app opens automatically at `http://localhost:8501`

---

## How to Use

**Sidebar controls:**
- Use the **month sliders** to filter the analysis period
- Change the **data seed** to regenerate a different dataset scenario

**Main panels:**
- **KPI Cards** — current month snapshot with delta vs. previous month
- **Trend Charts** — 12-month performance evolution with targets
- **Supplier Scorecard** — ranked table with conditional formatting
- **Route Map** — bubble chart: cost vs. days, sized by volume, colored by OTD

---

## Business Application

This dashboard maps directly to real logistics management tools:

| Dashboard element | Real-world equivalent |
|---|---|
| OTD tracking | Delivery performance in SAP SD / TM |
| Inventory turnover | Stock analysis in SAP MM (MMBE, MB52) |
| Supplier scorecard | Vendor evaluation in SAP MM (ME61) |
| Lead time monitoring | Purchasing info record in SAP MM |
| Freight cost per unit | Condition records in SAP TM / MM |

Understanding and visualizing these KPIs is core to supply chain consulting and SAP functional configuration.

---

## Tech Stack

| Tool | Use |
|---|---|
| Python 3.10+ | Core logic and data processing |
| Streamlit | Web app framework |
| Plotly | Interactive charts |
| pandas | Data manipulation |
| numpy | Synthetic data generation |

---

## Skills Demonstrated

- Supply chain KPI definition and monitoring
- Interactive data visualization for operations
- Dashboard design and UX for logistics teams
- Python scripting for analytics automation
- Synthetic data generation for prototyping

---

## About

**Emmanuel Beristain Guzmán**  
Logistics Engineer | Supply Chain Analytics | SAP Functional Trainee  
📍 México (Remote) · 📧 emmanuel.beristain.guzman@gmail.com  
🔗 [github.com/net421](https://github.com/net421)

---

*Part of a series of supply chain analytics projects. See also: EOQ/ROP inventory simulator, demand forecasting, and VRP route optimization.*

# Sales Analytics Projects

A collection of Python-based sales analytics scripts built as personal learning exercises — and as portfolio pieces to showcase during job interviews.

---

## Projects

### 1. Sales Funnel Analysis (`sales_funnel_analysis.py`)

Analyzes user behavior across a multi-stage e-commerce funnel (page view → add to cart → checkout → payment → purchase).

Key features:
- Stage-by-stage conversion rate calculation
- Drop-off analysis with visual breakdown
- Traffic source segmentation and performance comparison
- Time-to-conversion metrics per user journey
- Revenue dashboard with source attribution

### 2. Sales Performance Dashboard (`sales_performance_dashboard.py`)

A comprehensive monthly sales reporting script that covers revenue, growth, and team performance.

Key features:
- Core revenue metrics (gross profit, margin, AOV)
- Month-over-month and year-over-year growth tracking
- Regional performance breakdown
- Sales rep leaderboard (top 10)
- Product category analysis
- Executive summary dashboard with daily trend visualization

### 3. Customer Data Cleaning Pipeline (`customer_data_cleaning.py`)

A data wrangling pipeline that takes a raw customer CSV and produces a clean, validated, enriched dataset ready for analysis or CRM import.

Key features:
- Data quality audit (duplicates, missing values, invalid emails, out-of-range ages)
- Duplicate removal by composite key (`customer_id` + `email`)
- Text standardization — name casing, email normalization, whitespace trimming
- Missing value handling with meaningful defaults
- Invalid record filtering (broken emails, impossible ages)
- Feature engineering — `full_name`, `days_since_registration`
- Data quality flag (`Complete` / `Incomplete`) per record
- Before/after summary report and export to `clean_customers.csv`

A realistic sample dataset (`raw_customers.csv`) is included in the repo with intentional quality issues — duplicates, missing values, invalid emails, inconsistent casing, and extra whitespace — so the script can be run end-to-end without any external data.

---

### 4. Hotel Revenue Opportunity Simulation (`hotel_revenue_simulation.py`)

A sales-oriented simulation tool built for the hospitality industry. Takes hotel inputs (rooms, ADR, occupancy) and runs a Monte Carlo simulation to model potential revenue upside from improvements in AI visibility, review ratings, and response rate.

Key features:
- Monte Carlo simulation (10,000 iterations) across three revenue levers
- Conservative / Expected / Aggressive scenario output (P25, P50, P90)
- Branded PDF report generated with ReportLab — single-page A4 with header, metrics, scenario table, chart, and footer
- Stubbed API integration for an external AI visibility scoring service
- Google Colab compatible with one-click PDF download button

> A sample output PDF is included in the repo to show what the report looks like.

---

## Tech Stack

- **Python** — pandas, NumPy, Matplotlib, Seaborn, ReportLab, requests, ipywidgets
- Input: CSV files (events log, sales records, product catalog, customer data) / user prompts (hotel simulation)
- Environment: standard Python / Google Colab (hotel simulation)

## Sample Data

| File | Used by | Description |
|---|---|---|
| `raw_customers.csv` | Customer Data Cleaning | 312 rows with realistic quality issues built in |

The other scripts (funnel, sales dashboard) reference local paths from the original dev environment and would need to be pointed at your own data.

---

## About These Projects

These scripts were built as personal exercises to strengthen my data analytics and Python skills. The ideas and structure were inspired by things I came across online — articles, tutorials, and dashboards — combined with my own knowledge of sales operations. Parts of the code were developed with AI assistance.

The goal was to simulate real-world analytics workflows that I could discuss and demonstrate during interviews, covering areas like funnel analysis, KPI reporting, business intelligence, and probabilistic revenue modeling.

---

## Status

Work in progress — built for learning and portfolio purposes. Feedback welcome.

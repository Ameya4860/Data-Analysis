# Quant Developer Evaluation Assignment

## 📌 Project Title

**Real-Time Quantitative Analytics Dashboard using Binance Tick Data**

---

## 1️⃣ Architecture Diagram (draw.io)

See `architecture.drawio` for the source.
Architecture flow:
Binance WebSocket -> Python Ingestion -> In-Memory Buffer <-> SQLite -> Resampling -> Analytics (Core + Advanced) -> Streamlit Dashboard.

---

## 2️⃣ README.md (Final Version)

### 🚀 Overview

This project is a **real-time quantitative analytics dashboard** designed to ingest live tick data from Binance Futures, compute key statistical and trading analytics, and visualize them interactively. The system demonstrates an end-to-end pipeline from streaming data ingestion to live analytics and alerting, suitable for a quantitative trading or research environment.

### 🧱 Architecture

* **Data Ingestion:** Async WebSocket connection to Binance
* **Storage:** In-memory Pandas + SQLite persistence
* **Sampling:** 1-second, 1-minute, and 5-minute resampling
* **Analytics:** OLS regression, spread, z-score, ADF test, rolling correlation, Kalman Filter, Backtesting.
* **Frontend:** Streamlit + Plotly
* **Alerts:** Rule-based threshold alerts

### 📊 Analytics Implemented

* Price statistics
* Hedge ratio via OLS regression and Kalman Filter
* Spread computation
* Z-score (rolling mean & std)
* Augmented Dickey-Fuller (ADF) test
* Rolling correlation
* Backtesting Module
* Multi-symbol Heatmaps

### ⚙️ How to Run

1. Open a PowerShell terminal.
2. Run the master launcher script:
   ```powershell
   ./Start.ps1
   ```
   This will install dependencies, setup the database, start the ingestion service, analytics engines, and the dashboard.

### 📥 Data Export

* Download resampled data as CSV
* Download analytics outputs

### 🔔 Alerts

* User-defined z-score thresholds
* Real-time evaluation with UI notification

### 🧩 Extensibility

* New data feeds can be added without changing analytics
* New analytics modules can be plugged in
* Scalable to Kafka / Redis / ClickHouse

### 📌 Limitations

* Designed as a prototype
* Not production-hardened
* Single-machine execution

---

## 3️⃣ ChatGPT / AI Usage Disclosure (MANDATORY)

### 📄 Text to Include in README

> **AI Assistance Disclosure:**
>
> ChatGPT was used to assist with code structuring, architectural planning, analytics formulation, and documentation clarity. All generated code and designs were reviewed, modified, and validated by the author. The final implementation decisions, analytics logic, and system integration were performed manually.


###  Latest Feature Updates (Compliance)
* **OHLC Upload**: Added File Uploader to analyze external CSV data.
* **Live Controls**: Added Auto-Refresh toggle and Rolling Window slider.
* **On-Demand Analytics**: Added trigger button for ADF Test.

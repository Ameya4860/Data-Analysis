📊 Real-Time Quantitative Analytics Dashboard

Binance Futures | Live Market Analytics | Quant Research Prototype

🚀 Overview

This project is a real-time quantitative analytics dashboard built to demonstrate an end-to-end market data pipeline used in quantitative trading and research environments.

It ingests live tick data from Binance Futures via WebSockets, processes and resamples the data in real time, computes statistical and trading analytics, and visualizes the results through an interactive Streamlit dashboard.

The system is modular, extensible, and designed to closely resemble how professional quant research platforms are structured.

🧠 System Architecture

Refer to:

architecture.drawio – editable diagram

architecture.png – exported image

🔁 Data Flow
Binance WebSocket Feed
        ↓
Async Python Ingestion Service
        ↓
In-Memory Buffer (Pandas) ↔ SQLite (Persistent Storage)
        ↓
Resampling Engine (1s / 1m / 5m)
        ↓
Core Analytics Engine
        ↓
Advanced Analytics Modules
        ↓
Alert Engine
        ↓
Streamlit Dashboard

🧩 Design Rationale

Loosely coupled components

Analytics layer isolated for easy extension

Storage supports both real-time and historical replay

Scalable to Kafka / Redis / ClickHouse in future

📊 Analytics Implemented
🔹 Core Analytics

Price statistics

OLS hedge ratio (static)

Spread computation

Rolling Z-score

Rolling correlation

Augmented Dickey-Fuller (ADF) stationarity test

🔹 Advanced Analytics

Kalman Filter hedge ratio (dynamic)

Mean-reversion backtesting engine

Multi-symbol correlation heatmaps

🔔 Alerts

Rule-based alert engine

Live Z-score threshold monitoring

Visual notifications in the UI

🖥️ Frontend (Streamlit)

Live price metrics

Spread & Z-score charts

Statistical test execution (on-demand)

Backtest PnL visualization

Heatmap visualization

CSV export functionality

⚠️ UI updates in near-real-time using controlled refresh cycles
(This avoids performance issues common with tick-by-tick rendering.)

⚙️ How to Run the System
Prerequisites

Python 3.10+

PowerShell (Windows)

▶️ One-Command Startup
./Start.ps1


This script:

Creates virtual environment

Installs dependencies

Initializes SQLite database

Starts Binance ingestion

Launches Streamlit dashboard

Dashboard URL:

http://localhost:8501

📥 Data Input Options
✅ Live Mode

Binance Futures WebSocket

Multi-symbol support

✅ Offline Mode

Upload CSV OHLC data

Useful for backtesting and demos

📌 Project Structure
QuantAnalyticsDashboard/
├── Start.ps1
├── requirements.txt
├── config.yaml
├── README.md
├── architecture.drawio
├── architecture.png
├── CHATGPT_USAGE.md
│
├── src/
│   ├── ingestion/
│   ├── storage/
│   ├── analytics/
│   │   ├── core/
│   │   └── advanced/
│   ├── alerts/
│   └── frontend/
│
├── data/
├── logs/
└── tests/

📌 Limitations

Prototype / evaluation project

Not production-hardened

Single-machine execution

Streamlit UI uses pull-based refresh (not push streaming)

🧩 Extensibility

Plug in new data feeds (REST, CSV, CME)

Add new analytics modules easily

Can be upgraded to Kafka + FastAPI + React for true streaming UI

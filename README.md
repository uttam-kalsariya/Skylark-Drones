# Skylark Drones — Monday.com Business Intelligence Agent

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![API](https://img.shields.io/badge/API-monday.com_GraphQL_v2-0085FF.svg)](https://developer.monday.com/api-reference/docs)
[![AI Engine](https://img.shields.io/badge/LLM-Google_Gemini_3.5_Flash-4285F4.svg)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A conversational AI assistant designed for founders and executive leaders to query live business metrics from **monday.com** boards (**Work Orders** and **Deals**) dynamically via GraphQL API and Gemini 3.5 Flash tool-use.

---

## 🔗 Live Links

- **Live Prototype Demo**: [https://skylark-bi-agent.onrender.com](https://skylark-bi-agent.onrender.com) *(Paste deployed URL here)*
- **GitHub Repository**: [https://github.com/uttam-kalsariya/Skylark-Drones](https://github.com/uttam-kalsariya/Skylark-Drones)

---

## 📌 Table of Contents

- [Architecture Overview](#-architecture-overview)
- [Core Features](#-core-features)
- [monday.com Board Setup](#-mondaycom-board-setup)
- [How to Run Locally](#-how-to-run-locally)
- [Deployment Instructions](#-deployment-instructions)
- [Environment Variables Reference](#-environment-variables-reference)

---

## 🏗️ Architecture Overview

```text
+-----------------------------------------------------------------------+
|                       User (Streamlit Chat UI)                        |
+-----------------------------------------------------------------------+
                                   │
                                   ▼
+-----------------------------------------------------------------------+
|             Agent Orchestrator (agent.py - Gemini API)                |
|                    Function Calling & Tool Use                        |
+-----------------------------------------------------------------------+
                                   │
                                   ▼
+-----------------------------------------------------------------------+
|                      Tool: query_monday_board()                       |
+-----------------------------------------------------------------------+
                                   │
                 ┌─────────────────┴─────────────────┐
                 ▼                                   ▼
+---------------------------------+ +----------------------------------+
|     monday.com GraphQL API      | |      Data Resilience Layer       |
|       (monday_client.py)        | |        (data_cleaning.py)        |
+---------------------------------+ +----------------------------------+
                 │                                   │
                 ▼                                   ▼
+---------------------------------+ +----------------------------------+
|       Live Board Fetching       | |   Normalization & Quality Audit  |
|    (Items, Groups, Columns)     | | (Dates, Sectors, Values, Nulls) |
+---------------------------------+ +----------------------------------+
                 │                                   │
                 └─────────────────┬─────────────────┘
                                   ▼
+-----------------------------------------------------------------------+
|                 Cleaned Context & Quality Warnings                    |
+-----------------------------------------------------------------------+
                                   │
                                   ▼
+-----------------------------------------------------------------------+
|               Executive Insights & Leadership Summaries               |
+-----------------------------------------------------------------------+
```

---

## ✨ Core Features

- ⚡ **Live GraphQL Queries**: Dynamic data fetching on every turn with no stale caching.
- 🧹 **Resilient Data Cleaning**: Converts mixed dates, normalizes sector variants, strips currency strings, and drops duplicate embedded headers.
- 📊 **Executive Mode**: Structured leadership updates covering pipeline momentum, operational risks, and founder action items.
- 🎨 **Executive Light Theme**: Clean UI with sticky top header bar, session tracking, clear chat popover confirmation, and chat export (.md).

---

## 📋 monday.com Board Setup

### 1. Work Orders Board

| Column Name | Recommended Field Type | Details / Format |
| :--- | :--- | :--- |
| **Name** | Text | Item name / Work Order ID (e.g. `WO-1024 - Energy Site Survey`) |
| **Group** | Group | Operational status groups (e.g., `In Progress`, `Completed`, `Backlog`) |
| **Sector** | Status / Text | Sector classification (e.g., `Energy`, `Mining`, `Infrastructure`, `Agriculture`) |
| **Due Date** | Date | Target completion date (`YYYY-MM-DD`) |
| **Status** | Status / Text | Work order state (`Overdue`, `In Progress`, `Done`, `Blocked`) |
| **Budget / Value** | Currency / Number | Allocated contract value |

### 2. Deals Board

| Column Name | Recommended Field Type | Details / Format |
| :--- | :--- | :--- |
| **Name** | Text | Deal name (e.g., `Solar Panel Inspection - Acme Corp`) |
| **Group** | Group | Pipeline stages (e.g., `Lead`, `Negotiation`, `Closed Won`, `Closed Lost`) |
| **Sector** | Status / Text | Target industry (e.g., `Energy`, `Geospatial Services`, `Utilities`) |
| **Deal Value** | Currency / Number | Revenue opportunity size |
| **Close Date** | Date | Target closing date (`YYYY-MM-DD`) |

---

## 🚀 How to Run Locally

### Prerequisites

- Python 3.10+ installed
- Active monday.com API token and Google AI Studio API key

### 1. Clone Repository & Install Dependencies

```bash
git clone https://github.com/uttam-kalsariya/Skylark-Drones.git
cd Skylark-Drones
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Set your credentials inside `.env`:

```env
MONDAY_API_TOKEN=your_monday_api_token
GEMINI_API_KEY=AIzaSy...your_gemini_api_key
WORK_ORDERS_BOARD_ID=5030094931
DEALS_BOARD_ID=5030094796
```

### 3. Verify Live monday.com Data Connection

```bash
python monday_client.py
```

### 4. Launch Streamlit Application

```bash
python -m streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## ⚙️ Environment Variables Reference

| Variable Name | Required | Description |
| :--- | :--- | :--- |
| `MONDAY_API_TOKEN` | **Yes** | monday.com API v2 personal access token |
| `GEMINI_API_KEY` | **Yes** | Google AI Studio API key (starts with `AIzaSy...`) |
| `WORK_ORDERS_BOARD_ID` | **Yes** | Numeric Board ID for Work Orders |
| `DEALS_BOARD_ID` | **Yes** | Numeric Board ID for Deals |

---

## ☁️ Deployment Instructions (Render / Streamlit Cloud)

1. Push code to GitHub repository (`main` branch).
2. Create new Web Service on Render or Streamlit Community Cloud.
3. Configure build & start commands:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port $PORT`
4. Set Environment Variables in deployment platform dashboard:
   - `MONDAY_API_TOKEN`
   - `GEMINI_API_KEY`
   - `WORK_ORDERS_BOARD_ID`
   - `DEALS_BOARD_ID`

---

Built for Skylark Drones Technical Assignment.

# Skylark Drones — Monday.com Business Intelligence Agent

A conversational AI assistant designed for founders and executive leaders to query live business metrics from **monday.com** boards (**Work Orders** and **Deals**) dynamically via GraphQL API and Claude 3.5 Sonnet tool-use.

---

## 🏗️ Architecture Overview

```
                          User (Streamlit Chat UI)
                                     │
                                     ▼
                      Agent Orchestrator (agent.py)
                    Claude 3.5 Sonnet + Function Calling
                                     │
                                     ▼
                       Tool: query_monday_board()
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
      monday.com GraphQL API                  Data Resilience Layer
        (monday_client.py)                      (data_cleaning.py)
                 │                                       │
                 ▼                                       ▼
       Live Board Fetching                   Normalization & Quality Audit
    (Items, Groups, Columns)                (Dates, Sectors, Values, Nulls)
                 │                                       │
                 └───────────────────┬───────────────────┘
                                     ▼
                  Structured Context & Quality Warnings
                                     │
                                     ▼
                Executive Insights & Leadership Summaries
```

### Core Components
- **`app.py`**: Interactive Streamlit web interface maintaining multi-turn chat history and displaying real-time monday.com connection status & item counts in the sidebar.
- **`agent.py`**: Anthropic Claude 3.5 Sonnet orchestrator using tool calling (`query_monday_board`) to interpret founder questions, surface data quality caveats, and generate concise executive leadership updates.
- **`monday_client.py`**: Resilient GraphQL API v2 client featuring token authentication, rate limit/error handling, and cursor pagination (`items_page`).
- **`data_cleaning.py`**: Normalization layer that cleans messy text (e.g., sector name variations), parses inconsistent date formats into standard ISO `YYYY-MM-DD`, sanitizes monetary numbers, surfaces missing field counts, and degrades gracefully without throwing runtime exceptions.

---

## 📋 monday.com Board Setup Instructions

To ensure seamless integration, set up your monday.com boards with the following recommended column structure:

### 1. Work Orders Board
- **Name**: Item name / Work Order ID (e.g. `WO-1024 - Energy Site Survey`)
- **Group**: Operational status groups (e.g., `In Progress`, `Completed`, `Backlog`)
- **Columns**:
  - `Sector` (Status / Text): Sector classification (e.g., `Energy`, `Mining`, `Infrastructure`, `Agriculture`).
  - `Due Date` (Date): Target completion date (`YYYY-MM-DD` or standard date format).
  - `Status` (Status / Text): Work order state (`Overdue`, `In Progress`, `Done`, `Blocked`).
  - `Value` / `Budget` (Numbers / Currency): Allocated budget or contract value.

### 2. Deals Board
- **Name**: Deal name (e.g., `Solar Panel Inspection - Acme Corp`)
- **Group**: Pipeline stages (e.g., `Lead`, `Negotiation`, `Closed Won`, `Closed Lost`)
- **Columns**:
  - `Sector` (Status / Text): Target industry (e.g., `Energy`, `Geospatial Services`, `Utilities`).
  - `Deal Value` / `Amount` (Numbers / Currency): Revenue opportunity size.
  - `Expected Close Date` (Date): Target closing date.
  - `Owner` / `Rep` (People / Text): Account manager.

---

## 🚀 How to Run Locally

### Prerequisites
- Python 3.10+ installed.
- Active monday.com API token and Anthropic Claude API key.

### Step 1: Clone Repository & Install Dependencies
```bash
git clone https://github.com/uttam-kalsariya/Skylark-Drones.git
cd Skylark-Drones
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Fill in your credentials in `.env`:
```env
MONDAY_API_TOKEN=your_monday_api_token
ANTHROPIC_API_KEY=your_anthropic_api_key
WORK_ORDERS_BOARD_ID=your_work_orders_board_id
DEALS_BOARD_ID=your_deals_board_id
```

### Step 3: Test monday.com Connection
Verify live data fetching directly:
```bash
python monday_client.py
```

### Step 4: Launch Streamlit Web App
```bash
python -m streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## ☁️ Deployment Instructions (Streamlit Community Cloud)

1. Push your repository to GitHub (`main` branch).
2. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
3. Click **New app** and select:
   - **Repository**: `uttam-kalsariya/Skylark-Drones`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. Expand **Advanced Settings** -> **Secrets** and paste your `.env` variables:
   ```toml
   MONDAY_API_TOKEN = "your_monday_api_token"
   ANTHROPIC_API_KEY = "your_anthropic_api_key"
   WORK_ORDERS_BOARD_ID = "your_work_orders_board_id"
   DEALS_BOARD_ID = "your_deals_board_id"
   ```
5. Click **Deploy!**

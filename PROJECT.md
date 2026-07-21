# Skylark Drones — Monday.com Business Intelligence Agent

## Goal
Build a conversational AI agent that answers founder-level business intelligence
questions by querying live data from two monday.com boards: **Work Orders** and
**Deals**. No hardcoded CSV data — the agent must query monday.com dynamically
at runtime via API (or MCP).

## Example queries the agent must handle
- "How's our pipeline looking for the energy sector this quarter?"
- "Which work orders are overdue?"
- "What's our total deal value by sector?"
- "Give me a leadership update on Q3 performance."

## Core Requirements
1. **Monday.com Integration**
   - Connect via monday.com GraphQL API (or MCP).
   - Handle authentication via API token (stored in `.env`, never hardcoded).
   - Fetch live data from both boards on every query — no caching stale data.

2. **Data Resilience**
   - Handle missing/null values gracefully — never crash.
   - Normalize inconsistent date formats (multiple formats in source data).
   - Normalize inconsistent text fields (e.g. "Energy", "energy", "ENERGY ").
   - Track and surface data quality issues (e.g. "12 records had missing sector").

3. **Query Understanding**
   - Use an LLM (Claude API) with tool-use to interpret free-text founder questions.
   - Decide which board(s) and filters are relevant.
   - Ask a clarifying question when the request is ambiguous (e.g. undefined "this quarter").

4. **Business Intelligence**
   - Answer questions about revenue, pipeline health, sectoral performance,
     operational metrics (e.g. overdue work orders).
   - Cross-reference both boards when a question spans both.
   - Give insights and context, not raw table dumps.

5. **Leadership Update Mode (optional, implemented)**
   - When asked for a "leadership update" or "summary," the agent generates a
     clean 3–4 sentence executive-style paragraph instead of a conversational answer.

## Tech Stack
- **Backend**: Python
- **LLM / Agent**: Claude API (tool-use / function calling)
- **Data source**: monday.com GraphQL API
- **Frontend**: Streamlit (chat interface)
- **Hosting**: Streamlit Community Cloud
- **Secrets**: `.env` file (MONDAY_API_TOKEN, ANTHROPIC_API_KEY, board IDs) — never committed

## Architecture

```
User (Streamlit chat)
   |
   v
Agent Orchestrator (Claude API, tool-use)
   |
   |--> Tool: query_monday_board(board_name, filters)
   |         -> calls monday.com GraphQL API
   |         -> passes result through data cleaning layer
   |         -> returns cleaned, structured data + data-quality notes
   |
   v
Claude reasons over cleaned data -> generates insight-based answer
   (asks clarifying question if query is ambiguous)
```

## File Structure (target)
```
skylark-bi-agent/
├── PROJECT.md
├── README.md
├── DECISION_LOG.md
├── .env.example
├── requirements.txt
├── app.py                  # Streamlit chat UI
├── agent.py                # Claude agent + tool-use logic
├── monday_client.py         # monday.com GraphQL API wrapper
├── data_cleaning.py         # normalization / null handling
└── data/
    ├── Deal funnel Data.csv
    └── Work_Order_Tracker Data.csv
```

## Deliverables Checklist
- [ ] Hosted prototype link (Streamlit Cloud)
- [ ] Decision Log (2 pages max)
- [ ] Source code ZIP
- [ ] README with architecture + monday.com setup instructions
- [ ] Submitted via Google Form

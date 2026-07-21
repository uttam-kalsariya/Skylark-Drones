# Skylark Drones BI Agent — Technical Decision Log

## 1. Key Assumptions Made
- **Live Query Requirement**: Assumed business decision-making requires real-time data from monday.com rather than cached or static CSV dumps. Every user question triggers a live GraphQL fetch.
- **Board Structure Flexibility**: Assumed board structures across different teams may vary slightly in column titles and date formats. The system relies on semantic keyword matching and robust normalization rather than fragile hardcoded column IDs.
- **Ambiguous Quarter & Filter Definitions**: Assumed founder queries like "this quarter" or "energy sector pipeline" may contain implicit ambiguities. The agent is explicitly instructed to ask clarifying questions when context is incomplete rather than making silent assumptions.

---

## 2. Architectural Trade-offs & Rationale

### A. Direct GraphQL API vs. MCP (Model Context Protocol)
- **Decision**: Implemented direct integration with monday.com GraphQL API v2 via `requests` inside a custom Python tool rather than an external MCP server.
- **Why**: 
  - Direct API integration allows fine-grained control over GraphQL pagination (`items_page` cursor), error retry handling, and rate-limiting.
  - Keeps deployment lightweight for Streamlit Community Cloud without requiring external MCP process orchestration or protocol overhead.
  - Allows embedding custom data cleaning and quality audit metadata directly into the tool return payload before feeding context to Claude.

### B. Streamlit vs. Custom React/Next.js Frontend
- **Decision**: Built the chat application using Streamlit (`st.chat_message`, `st.chat_input`, `st.session_state`).
- **Why**:
  - Fast time-to-prototype with native Python integration.
  - Zero state-management boilerplates needed for multi-turn chat interactions.
  - Native support for real-time sidebar metrics (board item counts and connection health) and one-click deployment on Streamlit Community Cloud.

---

## 3. Leadership Updates: Interpretation & Implementation

### Interpretation
Founders and C-suite executives require immediate high-level strategic awareness without wading through dense tables or conversational chat fluff. A "leadership update" must synthesize operational health, revenue pipeline performance, key sector highlights, and critical risk areas into a concise summary.

### Implementation
- Added a dedicated prompt directive inside `agent.py`'s `SYSTEM_PROMPT`.
- When keywords like *"leadership update"*, *"executive summary"*, or *"summary"* are detected in user intent, Claude switches output mode from standard chat breakdown to a crisp, **3–4 sentence executive paragraph**.
- Structure of generated leadership update:
  1. Overall performance metric (total pipeline value / total active work orders).
  2. Sector breakdown highlight (e.g. Energy sector leading performance).
  3. Operational risk callout (e.g. overdue work orders needing immediate attention).
  4. Strategic next step / recommendation.

---

## 4. What I Would Do Differently With More Time

1. **Intelligent In-Memory Caching (TTL-based)**:
   - Implement short-lived TTL caching (e.g., 30–60 seconds) for raw GraphQL board queries to prevent API rate limit bottlenecks during rapid multi-turn chat sessions while keeping data fresh.
2. **Schema Auto-Discovery & Mapping UI**:
   - Add a UI configuration tab in Streamlit where administrators can map custom monday.com column IDs to standardized internal fields (`sector_column_id`, `value_column_id`, `due_date_column_id`).
3. **Interactive Charts & Trend Visualizations**:
   - Integrate `plotly` chart rendering alongside textual insights to visualize pipeline funnel stages, quarterly revenue trends, and work order completion velocity visually.
4. **Automated Unit & E2E Testing Suite**:
   - Create mock GraphQL fixture tests (`pytest`) covering edge cases in date parsing, currency symbol sanitization, and missing sector fallbacks.

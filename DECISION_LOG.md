# Skylark Drones BI Agent — Technical Decision Log

## 1. Key Assumptions Made

- **Live Query Requirement**: Assumed business decision-making requires real-time data from monday.com rather than cached or static CSV dumps. Every user question triggers a live GraphQL fetch.
- **Board Structure Flexibility**: Assumed board structures across different teams may vary slightly in column titles and date formats. The system relies on semantic keyword matching and robust normalization rather than fragile hardcoded column IDs.
- **Ambiguous Quarter & Filter Definitions**: Assumed founder queries like *"this quarter"* or *"energy sector pipeline"* may contain implicit ambiguities. The agent is explicitly instructed to provide immediate overall live data first and offer 2-3 structured follow-up choices.

---

## 2. Architectural Trade-offs & Rationale

### A. Direct GraphQL API vs. MCP (Model Context Protocol)
- **Decision**: Implemented direct integration with monday.com GraphQL API v2 via `requests` inside a custom Python tool rather than an external MCP server.
- **Why**:
  - Direct API integration allows fine-grained control over GraphQL pagination (`items_page` cursor), error retry handling, and rate-limiting.
  - Keeps deployment lightweight for hosting platforms without requiring external MCP process orchestration.
  - Allows embedding custom data cleaning and quality audit metadata directly into the tool return payload before feeding context to Gemini.

### B. Streamlit vs. Custom React/Next.js Frontend
- **Decision**: Built the chat application using Streamlit (`st.chat_message`, `st.chat_input`, `st.session_state`).
- **Why**:
  - Fast time-to-prototype with native Python integration.
  - Zero state-management boilerplates needed for multi-turn chat interactions.
  - Native support for real-time sidebar metrics (board item counts and connection health) and effortless deployment.

---

## 3. Leadership Updates: Interpretation & Implementation

### Interpretation
Founders and C-suite executives require immediate high-level strategic awareness without wading through dense tables or conversational chat fluff. A "leadership update" must synthesize operational health, revenue pipeline performance, key sector highlights, and critical risk areas into a concise summary.

### Implementation
- Added a dedicated prompt directive inside `agent.py`'s `SYSTEM_PROMPT`.
- When keywords like *"leadership update"*, *"executive summary"*, or *"summary"* are detected in user intent, Gemini structures output into 3 distinct sections:
  1. 📊 **Executive Overview**: Total pipeline value and lead momentum.
  2. ⚡ **Operations & Risks**: Active work orders, overdue tasks, and data gaps.
  3. 🎯 **Strategic Next Steps**: Concrete founder recommendations.

---

## 4. What I Would Do Differently With More Time

1. **Intelligent In-Memory Caching (TTL-based)**:
   - Implement short-lived TTL caching (e.g., 30–60 seconds) for raw GraphQL board queries to prevent API rate limit bottlenecks during rapid multi-turn chat sessions.
2. **Schema Auto-Discovery & Mapping UI**:
   - Add a UI configuration tab in Streamlit where administrators can map custom monday.com column IDs to standardized internal fields (`sector_column_id`, `value_column_id`, `due_date_column_id`).
3. **Interactive Charts & Visual Analytics**:
   - Integrate `plotly` chart rendering alongside textual insights to visualize pipeline funnel stages and work order completion velocity visually.
4. **Automated Unit & E2E Testing Suite**:
   - Create mock GraphQL fixture tests (`pytest`) covering edge cases in date parsing, currency sanitization, and missing sector fallbacks.

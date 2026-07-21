"""
Conversational AI Agent Orchestrator for Skylark Drones BI Agent.

Responsible for:
- Interfacing with Claude API with tool-use capabilities.
- Interpreting free-text founder questions and querying monday.com boards.
- Data quality surfacing and clarifying ambiguous user requests.
- Executive Leadership Update mode for concise 3-4 sentence updates.
"""

import json
import os
from typing import Any, Dict, List, Optional
import anthropic
from dotenv import load_dotenv

import data_cleaning
import monday_client

load_dotenv()

SYSTEM_PROMPT = """You are a Business Intelligence Agent for Skylark Drones founders. Your goal is to provide accurate, executive-level insights on revenue, sales pipeline health, sector performance, and operational work orders using live data queried from monday.com.

Guidelines:
1. Data Queries: Use the `query_monday_board` tool to retrieve live data from 'work_orders' or 'deals' boards. Always fetch live data when answering questions requiring board metrics.
2. Data Quality & Resilience: Explicitly surface relevant data quality warnings (e.g., missing sectors, unparseable dates, zero deal values) when presenting your conclusions.
3. Ambiguity: If a user query is ambiguous (e.g. unspecified time range like 'this quarter' or unclear filters), ask a polite clarifying question.
4. Leadership Update Mode: If the user asks for a 'leadership update', 'executive update', or 'summary', answer with a crisp 3-4 sentence executive paragraph highlighting key metrics, pipeline health, operational status, and primary risk/opportunity, rather than standard chat bullet points.
5. Provide actionable insights and context, never raw unformatted data dumps."""

TOOLS = [
    {
        "name": "query_monday_board",
        "description": "Fetch live data from monday.com boards ('work_orders' or 'deals') and apply cleaning & data quality metrics.",
        "input_schema": {
            "type": "object",
            "properties": {
                "board_name": {
                    "type": "string",
                    "enum": ["work_orders", "deals"],
                    "description": "The target monday.com board to query."
                },
                "filters": {
                    "type": "object",
                    "description": "Optional key-value filters to narrow down records (e.g. {'sector': 'Energy', 'status': 'Overdue'})."
                }
            },
            "required": ["board_name"]
        }
    }
]


def query_monday_board(board_name: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Query raw items from a monday.com board, clean records, surface data quality,
    and optionally filter records.
    """
    if board_name == "work_orders":
        board_id = os.getenv("WORK_ORDERS_BOARD_ID")
    elif board_name == "deals":
        board_id = os.getenv("DEALS_BOARD_ID")
    else:
        return {"error": f"Invalid board_name '{board_name}'. Must be 'work_orders' or 'deals'."}

    if not board_id:
        try:
            boards = monday_client.list_boards()
            for b in boards:
                b_name = b.get("name", "").lower()
                if board_name == "work_orders" and ("work" in b_name or "order" in b_name):
                    board_id = b["id"]
                    break
                elif board_name == "deals" and ("deal" in b_name or "funnel" in b_name or "pipe" in b_name):
                    board_id = b["id"]
                    break
            if not board_id and boards:
                board_id = boards[0]["id"]
        except Exception as e:
            return {"error": f"Failed to list boards to find '{board_name}': {e}"}

    if not board_id:
        return {"error": f"Board ID for '{board_name}' is not configured in .env and could not be resolved."}

    try:
        raw_items = monday_client.get_board_items(board_id)
        cleaned_records, quality_report = data_cleaning.clean_records(raw_items)
        cleaned_result = {
            "board_name": board_name,
            "total_records": len(cleaned_records),
            "cleaned_records": cleaned_records,
            "data_quality_report": quality_report,
        }

        if filters and cleaned_result.get("cleaned_records"):
            filtered_records = []
            for rec in cleaned_result["cleaned_records"]:
                cols = rec.get("columns", {})
                match = True
                for f_key, f_val in filters.items():
                    if f_val is None:
                        continue
                    f_key_lower = str(f_key).lower()
                    found_val = None
                    for col_k, col_v in cols.items():
                        if f_key_lower in col_k.lower():
                            found_val = col_v
                            break
                    if found_val is None or str(f_val).lower() not in str(found_val).lower():
                        match = False
                        break
                if match:
                    filtered_records.append(rec)
            cleaned_result["cleaned_records"] = filtered_records
            cleaned_result["filtered_count"] = len(filtered_records)

        return cleaned_result
    except Exception as err:
        return {"error": f"Failed to query board '{board_name}': {err}"}


def execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> str:
    """Execute local python tool functions requested by Claude."""
    if tool_name == "query_monday_board":
        board_name = tool_args.get("board_name")
        filters = tool_args.get("filters")
        result = query_monday_board(board_name=board_name, filters=filters)
        return json.dumps(result)
    return json.dumps({"error": f"Unknown tool: {tool_name}"})


def run_agent(user_message: str, conversation_history: Optional[List[Dict[str, Any]]] = None) -> str:
    """
    Run the BI agent orchestrator.
    
    Args:
        user_message: The latest prompt from the user.
        conversation_history: Optional list of previous chat messages.
        
    Returns:
        The final textual response from Claude.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is missing. Please set it in your .env file.")

    client = anthropic.Anthropic(api_key=api_key)

    messages: List[Dict[str, Any]] = []
    if conversation_history:
        for msg in conversation_history:
            messages.append({"role": msg["role"], "content": msg["content"]})
            
    messages.append({"role": "user", "content": user_message})

    # Call Claude API with tool-use loop
    while True:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=messages,
            tools=TOOLS,
        )

        if response.stop_reason == "tool_use":
            # Append assistant message with tool calls
            messages.append({"role": "assistant", "content": response.content})

            # Process each tool call and respond with tool_result content
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_output = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": tool_output,
                    })

            messages.append({"role": "user", "content": tool_results})
        else:
            # Extract text from response blocks
            final_text = ""
            for block in response.content:
                if block.type == "text":
                    final_text += block.text
            return final_text


if __name__ == "__main__":
    print("Testing agent module...")
    sample_query = "Give me a quick test overview of our work orders."
    try:
        ans = run_agent(sample_query)
        print(f"\nResponse:\n{ans}")
    except Exception as e:
        print(f"[Agent Execution Error] {e}")

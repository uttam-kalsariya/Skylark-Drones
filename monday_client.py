"""
Monday.com GraphQL API Integration Module for Skylark Drones BI Agent.

Responsible for:
- Connecting to monday.com via GraphQL API v2 using token authentication.
- Dynamically querying live board data with cursor pagination.
- Handling API errors (authentication failures, rate limits, network errors, GraphQL errors).
"""

import os
from typing import Any, Dict, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

MONDAY_API_URL = "https://api.monday.com/v2"


def _get_headers() -> Dict[str, str]:
    """Retrieve API authorization headers from environment variables."""
    token = os.getenv("MONDAY_API_TOKEN")
    if not token:
        raise ValueError(
            "MONDAY_API_TOKEN is missing. Please set it in your .env file."
        )
    return {
        "Authorization": token,
        "Content-Type": "application/json",
        "API-Version": "2023-10",
    }


def _make_graphql_query(query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Execute a GraphQL query against monday.com API v2 with error handling.
    """
    headers = _get_headers()
    payload: Dict[str, Any] = {"query": query}
    if variables:
        payload["variables"] = variables

    try:
        response = requests.post(MONDAY_API_URL, json=payload, headers=headers, timeout=30)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Network error connecting to monday.com API: {e}") from e

    if response.status_code == 401:
        raise PermissionError(
            "monday.com API token authentication failed (401 Unauthorized). "
            "Please check your MONDAY_API_TOKEN in .env."
        )
    elif response.status_code == 429:
        raise RuntimeError(
            "monday.com API rate limit exceeded (429 Too Many Requests). "
            "Please wait before trying again."
        )
    elif response.status_code >= 500:
        raise RuntimeError(
            f"monday.com API server error (HTTP {response.status_code}): {response.text}"
        )
    elif response.status_code != 200:
        raise RuntimeError(
            f"monday.com API returned unexpected HTTP status {response.status_code}: {response.text}"
        )

    res_json = response.json()
    if "errors" in res_json:
        error_msgs = [err.get("message", str(err)) for err in res_json["errors"]]
        raise RuntimeError(f"monday.com GraphQL API returned error(s): {'; '.join(error_msgs)}")

    return res_json.get("data", {})


def list_boards() -> List[Dict[str, str]]:
    """
    List available boards accessible by the MONDAY_API_TOKEN.
    
    Returns:
        List of dicts containing 'id' and 'name' for each board.
    """
    query = """
    query {
      boards(limit: 100) {
        id
        name
        state
      }
    }
    """
    data = _make_graphql_query(query)
    boards = data.get("boards", [])
    return [{"id": str(b.get("id")), "name": b.get("name", "")} for b in boards]


def get_board_items(board_id: str | int) -> List[Dict[str, Any]]:
    """
    Fetch all items from a monday.com board using GraphQL API v2 cursor pagination.
    
    Args:
        board_id: The unique ID of the monday.com board.
        
    Returns:
        List of dicts, where each dict represents an item with id, name, group,
        column_values, and a simplified columns dict (title -> text).
    """
    board_id_str = str(board_id)
    all_items: List[Dict[str, Any]] = []
    cursor: Optional[str] = None

    query = """
    query GetBoardItems($board_id: [ID!], $cursor: String) {
      boards(ids: $board_id) {
        id
        name
        items_page(limit: 100, cursor: $cursor) {
          cursor
          items {
            id
            name
            updated_at
            group {
              id
              title
            }
            column_values {
              id
              title
              text
              value
              type
            }
          }
        }
      }
    }
    """

    while True:
        variables: Dict[str, Any] = {"board_id": [board_id_str]}
        if cursor:
            variables["cursor"] = cursor

        data = _make_graphql_query(query, variables)
        boards = data.get("boards", [])
        if not boards:
            break

        items_page = boards[0].get("items_page", {})
        items = items_page.get("items", [])

        for item in items:
            col_vals = item.get("column_values", [])
            columns_dict = {}
            for col in col_vals:
                title = col.get("title")
                if title:
                    columns_dict[title] = col.get("text")

            formatted_item = {
                "id": item.get("id"),
                "name": item.get("name"),
                "group": item.get("group", {}).get("title") if item.get("group") else None,
                "updated_at": item.get("updated_at"),
                "column_values": col_vals,
                "columns": columns_dict,
            }
            all_items.append(formatted_item)

        cursor = items_page.get("cursor")
        if not cursor or not items:
            break

    return all_items


if __name__ == "__main__":
    print("Testing monday.com API client...")
    try:
        print("\n--- Listing Boards ---")
        boards = list_boards()
        if not boards:
            print("No boards found or MONDAY_API_TOKEN does not have access.")
        else:
            for b in boards:
                print(f"Board ID: {b['id']} | Name: {b['name']}")

        target_board_id = os.getenv("WORK_ORDERS_BOARD_ID") or os.getenv("DEALS_BOARD_ID")
        if not target_board_id and boards:
            target_board_id = boards[0]["id"]

        if target_board_id:
            print(f"\n--- Fetching First 5 Items for Board ID: {target_board_id} ---")
            items = get_board_items(target_board_id)
            print(f"Total items fetched: {len(items)}")
            print("\nFirst 5 items sample:")
            for item in items[:5]:
                print(f"\n[Item ID: {item['id']}] {item['name']}")
                print(f"  Group: {item['group']}")
                print(f"  Columns: {item['columns']}")
        else:
            print("\nNo board ID specified in .env and no boards returned from account.")
    except Exception as err:
        print(f"\n[monday_client Error] {err}")


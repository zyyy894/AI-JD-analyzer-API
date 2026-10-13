from typing import Any, Dict, List, TypedDict


class AgentState(TypedDict):
    user_id: str
    user_input: str
    intent: str
    tool_results: List[Dict[str, Any]]
    final_answer: str
    markdown_report: str

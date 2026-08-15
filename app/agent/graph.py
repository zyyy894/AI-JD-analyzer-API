from langgraph.graph import END, START, StateGraph

from app.agent.state import AgentState
from app.agent.tools import (
    analyze_job_description,
    export_markdown,
    generate_report,
    search_knowledge_base,
)


def intent_node(state: AgentState):
    user_input = state["user_input"]

    if "JD" in user_input or "岗位" in user_input:
        intent = "job_plan"
    elif "知识库" in user_input or "学习计划" in user_input:
        intent = "knowledge_plan"
    else:
        intent = "general"

    return {"intent": intent}


def route_by_intent(state: AgentState):
    if state["intent"] == "job_plan":
        return "job_tool_node"

    if state["intent"] == "knowledge_plan":
        return "knowledge_tool_node"

    return "report_node"


def knowledge_tool_node(state: AgentState):
    result = search_knowledge_base(state["user_input"], top_k=3)

    return {
        "tool_results": [
            {
                "tool": "search_knowledge_base",
                "result": result,
            }
        ]
    }


def job_tool_node(state: AgentState):
    result = analyze_job_description(state["user_input"])

    return {
        "tool_results": [
            {
                "tool": "analyze_job_description",
                "result": result,
            }
        ]
    }


def report_node(state: AgentState):
    report = generate_report(
        task=state["user_input"],
        tool_results=state.get("tool_results", []),
    )

    return {"final_answer": report}


def markdown_node(state: AgentState):
    markdown = export_markdown(
        title="Agent 生成报告",
        content=state["final_answer"],
    )

    return {"markdown_report": markdown}


def build_agent_graph():
    graph = StateGraph(AgentState)

    graph.add_node("intent_node", intent_node)
    graph.add_node("knowledge_tool_node", knowledge_tool_node)
    graph.add_node("job_tool_node", job_tool_node)
    graph.add_node("report_node", report_node)
    graph.add_node("markdown_node", markdown_node)

    graph.add_edge(START, "intent_node")

    graph.add_conditional_edges(
        "intent_node",
        route_by_intent,
        {
            "knowledge_tool_node": "knowledge_tool_node",
            "job_tool_node": "job_tool_node",
            "report_node": "report_node",
        },
    )

    graph.add_edge("knowledge_tool_node", "report_node")
    graph.add_edge("job_tool_node", "report_node")
    graph.add_edge("report_node", "markdown_node")
    graph.add_edge("markdown_node", END)

    return graph.compile()
from langgraph.graph import END, START, StateGraph
from app.agent.state import AgentState


def start_node(state: AgentState):
    return {
        "final_answer": "收到任务：" + state["user_input"]
    }


graph = StateGraph(AgentState)
graph.add_node("start_node", start_node)
graph.add_edge(START, "start_node")
graph.add_edge("start_node", END)

app = graph.compile()

result = app.invoke({
    "user_input": "帮我生成学习计划",
    "intent": "",
    "tool_results": [],
    "final_answer": "",
    "markdown_report": "",
})

print(result)
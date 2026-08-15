from app.agent.graph import build_agent_graph

agent_app = build_agent_graph()

result = agent_app.invoke({
    "user_input": "根据知识库内容，生成一份RAG学习计划",
    "intent": "",
    "tool_results": [],
    "final_answer": "",
    "markdown_report": "",
})

print(result)
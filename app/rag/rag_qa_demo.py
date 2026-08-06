from app.rag.rag_service import RagService


text = """
AI智能体开发工程师需要熟悉 Python、FastAPI、RAG、Agent、LangGraph。
岗位要求理解 Prompt Engineering、工具调用和上下文管理。
RAG系统需要先把文档切分成片段，再进行向量化和相似度检索。
向量数据库可以根据用户问题检索相关内容。
"""


rag_service = RagService()

# 先写入知识库
chunks = rag_service.ingest_text(text)
print(f"已写入 {len(chunks)} 个文本片段")

# 再提问
question = "AI智能体岗位需要掌握哪些技术？"

result = rag_service.ask(
    question=question,
    top_k=3
)

print("\n回答：")
print(result["answer"])

print("\n参考资料：")
for index, source in enumerate(result["sources"], start=1):
    print(f"{index}. {source}")
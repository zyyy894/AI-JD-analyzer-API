from app.rag.splitter import split_text
from app.rag.vector_store import VectorStore


text = """
AI智能体开发工程师需要熟悉 Python、FastAPI、RAG、Agent、LangGraph。
岗位要求理解 Prompt Engineering、工具调用和上下文管理。
RAG系统需要先把文档切分成片段，再进行向量化和相似度检索。
向量数据库可以根据用户问题检索相关内容。
LangGraph可以用来编排智能体工作流。
有向量数据库、知识库问答、自动化测试经验者优先。
篮球比赛需要团队配合和战术执行。
"""

chunks = split_text(
    text,
    chunk_size=60,
    chunk_overlap=15
)

print("切分后的 chunks：")
for index, chunk in enumerate(chunks, start=1):
    print(f"{index}. {chunk}")

vector_store = VectorStore(
    persist_path="./chroma_db",
    collection_name="job_docs"
)

vector_store.add_texts(chunks)

question = "AI智能体岗位需要掌握哪些技术？"

results = vector_store.search(
    query=question,
    top_k=3
)

print("\n问题：")
print(question)

print("\n检索结果：")
for index, doc in enumerate(results, start=1):
    print(f"{index}. {doc}")
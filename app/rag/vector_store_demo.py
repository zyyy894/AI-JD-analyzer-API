import chromadb

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(name="job_docs")

documents = [
    "AI智能体开发工程师需要熟悉 Python、FastAPI、RAG、Agent、LangGraph。",
    "岗位要求理解 Prompt Engineering、工具调用和上下文管理。",
    "有向量数据库、知识库问答、自动化测试经验者优先。",
    "篮球比赛需要团队配合和战术执行。"
]

ids = ["doc1", "doc2", "doc3", "doc4"]

collection.upsert(
    documents=documents,
    ids=ids
)

question = "AI智能体岗位需要哪些技术？"

results = collection.query(
    query_texts=[question],
    n_results=2
)

print(f"问题：{question}")
print("检索结果：")

for index, doc in enumerate(results["documents"][0], start=1):
    print(f"{index}. {doc}")

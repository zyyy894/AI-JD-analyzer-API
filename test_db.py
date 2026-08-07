from app.services.db_service import init_db, list_documents, list_qa_history

init_db()

print("documents:")
documents = list_documents()
for item in documents:
    print(item)

print("\nqa_history:")
history = list_qa_history()
for item in history:
    print(item)
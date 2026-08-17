import requests

BASE_URL = "http://127.0.0.1:8001"


def test_health():
    response = requests.get(f"{BASE_URL}/health")
    print("health:", response.json())


def test_agent():
    payload = {
        "task": "根据知识库内容，生成一份RAG学习计划"
    }

    response = requests.post(f"{BASE_URL}/agent/run", json=payload)
    print("agent:", response.json())


if __name__ == "__main__":
    test_health()
    test_agent()
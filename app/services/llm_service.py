import os
from openai import OpenAI
from dotenv import load_dotenv

from app.settings import ENV_FILE

load_dotenv(dotenv_path=ENV_FILE)

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
)


def call_llm(prompt: str) -> str:
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "你是一名AI应用开发求职导师，擅长分析岗位JD并给出结构化学习建议。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content

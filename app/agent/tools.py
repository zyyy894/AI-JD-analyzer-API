from app.rag.rag_service import RagService
from app.services.llm_service import call_llm
from app.services.prompt_service import build_jd_analyze_prompt

rag_service = RagService()


def search_knowledge_base(query: str, top_k: int = 3, *, user_id: str) -> dict:
    return rag_service.ask(question=query, top_k=top_k, user_id=user_id)


def analyze_job_description(jd: str) -> str:
    prompt = build_jd_analyze_prompt(jd)
    return call_llm(prompt)


def summarize_document(content: str) -> str:
    prompt = f"""
请总结下面的文档内容，提炼核心知识点：

{content}
"""
    return call_llm(prompt)


def generate_report(task: str, tool_results: list) -> str:
    prompt = f"""
请根据用户任务和工具结果，生成一份结构清晰的学习计划。

用户任务：
{task}

工具结果：
{tool_results}

请输出：
1. 目标
2. 学习重点
3. 每日安排
4. 项目实践
5. 总结建议
"""
    return call_llm(prompt)


def export_markdown(title: str, content: str) -> str:
    return f"# {title}\n\n{content}"

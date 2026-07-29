def build_jd_analyze_prompt(jd: str) -> str:
    return f"""
你是一名AI应用开发求职导师，请分析下面的岗位JD。

岗位JD：
{jd}

请严格按照下面JSON格式输出，不要输出多余解释：

{{
  "core_skills": ["核心技能1", "核心技能2"],
  "bonus_skills": ["加分项1", "加分项2"],
  "learning_plan": ["学习建议1", "学习建议2", "学习建议3"],
  "resume_keywords": ["简历关键词1", "简历关键词2"],
  "summary": "一句话总结这个岗位的能力要求"
}}
"""
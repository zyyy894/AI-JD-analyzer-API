import json
import re

from app.schemas import ResumeJDMatchResult
from app.services.llm_service import call_llm


def build_match_prompt(resume: str, jd: str) -> str:
    return f"""
Compare the resume with the job description using only evidence present in the resume.
Do not invent skills, experience, education, or achievements. Return JSON only with this exact schema:
{{
  "match_score": 0,
  "matching_skills": [],
  "missing_skills": [],
  "strengths": [],
  "gaps": [],
  "recommendations": [],
  "summary": ""
}}
match_score must be a number from 0 to 100. A skill is matching only when the resume supports it.

RESUME:
{resume}

JOB DESCRIPTION:
{jd}
"""


def parse_match_result(raw: str) -> ResumeJDMatchResult:
    text = raw.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.IGNORECASE | re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()
    try:
        return ResumeJDMatchResult.model_validate(json.loads(text))
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise ValueError("Model output failed resume-JD match validation") from exc


def match_resume_to_jd(resume: str, jd: str) -> dict:
    return parse_match_result(call_llm(build_match_prompt(resume, jd))).model_dump()

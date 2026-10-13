from typing import Any

from pydantic import BaseModel, Field, field_validator


class JDAnalyzeRequest(BaseModel):
    jd: str = Field(..., min_length=1, description="岗位描述")


class RagIngestRequest(BaseModel):
    text: str = Field(..., min_length=1, description="知识库文本")


class RagAskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="用户问题")
    top_k: int = Field(default=3, ge=1, le=10, description="返回结果数量")


class ApiResponse(BaseModel):
    code: int
    message: str
    data: Any = None


class JDAnalyzeResult(BaseModel):
    core_skills: list[str]
    bonus_skills: list[str]
    learning_plan: list[str]
    resume_keywords: list[str]
    summary: str = Field(min_length=1)


class ResumeJDMatchResult(BaseModel):
    match_score: float = Field(ge=0, le=100)
    matching_skills: list[str]
    missing_skills: list[str]
    strengths: list[str]
    gaps: list[str]
    recommendations: list[str]
    summary: str = Field(min_length=1)


class AgentRequest(BaseModel):
    task: str = Field(..., min_length=1, description="用户输入任务")


class UserRegister(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str):
        import re
        value = value.strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("邮箱格式不正确")
        return value


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)

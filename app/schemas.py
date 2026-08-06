from typing import Any
from pydantic import BaseModel, Field


class JDAnalyzeRequest(BaseModel):
    jd: str = Field(..., min_length=1, description="岗位描述")
class RagIngestRequest(BaseModel):
    text: str = Field(..., min_length=1, description="知识库文本")


class RagAskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="用户问题")
    top_k: int = Field(default=3, ge=1, le=10, description="检索数量")


class ApiResponse(BaseModel):
    code: int
    message: str
    data: Any = None

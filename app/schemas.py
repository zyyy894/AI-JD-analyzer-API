from typing import Any
from pydantic import BaseModel, Field


class JDAnalyzeRequest(BaseModel):
    jd: str = Field(..., min_length=1, description="岗位描述")


class ApiResponse(BaseModel):
    code: int
    message: str
    data: Any = None
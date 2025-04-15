# app/models.py
from pydantic import BaseModel

# 공통 응답 모델 정의
class ApiResponse(BaseModel):
    code: str
    data: dict

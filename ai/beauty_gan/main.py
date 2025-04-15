# main.py
from fastapi import FastAPI
from app.api import router
from app.exceptions import custom_http_exception_handler

# FastAPI 앱 생성
app = FastAPI()

# 라우터 등록
app.include_router(router)

# 예외 핸들러 등록
app.add_exception_handler(Exception, custom_http_exception_handler)
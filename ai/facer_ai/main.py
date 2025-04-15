from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from app.api import router
from app.cache import start_cache_cleanup_thread
from app.exceptions import custom_http_exception_handler, CustomHTTPException

# 앱 시작 시 백그라운드에서 캐시 정리 쓰레드를 실행하는 lifespan 설정
@asynccontextmanager
async def lifespan(app: FastAPI):
    start_cache_cleanup_thread()
    yield

# FastAPI 인스턴스 생성 및 lifespan 설정
app = FastAPI(lifespan=lifespan)

# 라우터 등록
app.include_router(router)

#  전역 에러 핸들러 등록
@app.exception_handler(CustomHTTPException)
async def handler(request: Request, exc: CustomHTTPException):
    return await custom_http_exception_handler(request, exc)
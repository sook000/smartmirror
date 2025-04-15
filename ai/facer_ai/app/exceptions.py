from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging

# 로거 생성
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# 커스텀 예외 클래스
class CustomHTTPException(HTTPException):
    def __init__(self, code: str, status_code: int, detail: str = None):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code
        logger.error(f"Error Code: {code}, Status Code: {status_code}, Detail: {detail}")

# 공통 응답 생성 함수
def create_response(code: str, data: dict, status_code: int = 200) -> JSONResponse:
    return JSONResponse(content={"code": code, "data": data}, status_code=status_code)

# 커스텀 예외 처리 핸들러
async def custom_http_exception_handler(request: Request, exc: CustomHTTPException):
    return create_response(exc.code, None, status_code=exc.status_code)
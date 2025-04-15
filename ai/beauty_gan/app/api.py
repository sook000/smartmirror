# app/api.py
from fastapi import APIRouter, UploadFile, Form, File
from app.handler import apply_makeup

router = APIRouter()

# /ai/makeup 라우터
@router.post("/ai/makeup")
async def makeup_endpoint(
    inputImage: UploadFile = File(...),
    styleImage: str = Form(...)
):
    return await apply_makeup(inputImage, styleImage)
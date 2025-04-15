from fastapi import APIRouter, File, UploadFile, Form, Request
from PIL import Image, UnidentifiedImageError
import numpy as np, hashlib, os, io, base64, json, cv2
from .exceptions import CustomHTTPException, create_response, custom_http_exception_handler
from .models import ApiResponse
from .cache import segmentation_cache_dir
from .preprocessing import detect_and_crop_largest_face
from .segmentation import segment_face
from .colorize import apply_color_changes

router = APIRouter()

@router.post("/ai/custom")
async def parse_face(
    inputImage: UploadFile = File(...),
    eyebrowColor: str = Form(None),
    skinColor: str = Form(None),
    lipColor: str = Form(None),
    lipMode: str = Form(None)
):
    # inputImage가 없거나 비어 있는 경우 예외 처리
    if not inputImage:
        raise CustomHTTPException("F02", 400, "Inputimage missing")

    try:
        # 이미지를 읽어서 numpy 배열로 변환
        image_bytes = await inputImage.read()
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        image_np = np.array(image)

        # 입력 이미지의 해시 생성
        image_hash = hashlib.md5(image_bytes).hexdigest()
        seg_path = os.path.join(segmentation_cache_dir, f"{image_hash}_seg.npy")
       
        # 캐시에 세그멘테이션 결과가 있는지 확인
        if os.path.exists(seg_path):
            seg_result = np.load(seg_path)
            
            # 크롭 정보를 불러와 이미지 크롭 
            with open(os.path.join(segmentation_cache_dir, f"{image_hash}_cropinfo.json"), "r") as f:
                x1, y1, w, h = json.load(f)
            cropped = image_np[y1:y1 + h, x1:x1 + w]
            
            # 크롭된 이미지를 고정된 크기(500x500)로 리사이즈
            image_np = cv2.resize(cropped, (500, 500), interpolation=cv2.INTER_AREA)
        # 파일 없다면 이미지 크롭 후 새그멘테이션 수행 
        else:
            image_np, crop_info = detect_and_crop_largest_face(image_np)
            seg_result = segment_face(image_np, image_hash, crop_info)

    except UnidentifiedImageError:
        # 이미지 형식이 잘못된 경우 예외 처리
        raise CustomHTTPException("F00", 400, "Invalid input image format")
    except Exception as e:
        raise CustomHTTPException("G00", 500, f"Error during face segmentation: {e}")

    try:
        # 색상 값을 처리
        eyebrowColor = np.array([int(x) for x in eyebrowColor.split(',')], dtype=np.float32) if eyebrowColor else None
        skinColor = np.array([int(x) for x in skinColor.split(',')], dtype=np.float32) if skinColor else None
        lipColor = np.array([int(x) for x in lipColor.split(',')], dtype=np.float32) if lipColor else None

        # 색상 변경 적용
        result_img = apply_color_changes(image_np, seg_result, eyebrowColor, skinColor, lipColor, lipMode)
        
        # 이미지 BGR -> RGB로 변환 및 base64로 인코딩
        result_img = result_img.astype(np.uint8)
        pil_img = Image.fromarray(result_img)
        buffer = io.BytesIO()
        pil_img.save(buffer, format="JPEG")
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return create_response("A00", {"makeupImage": img_str}, 200)
    
    except ValueError as ve:
            # 색상 값 변환 오류 처리
            raise CustomHTTPException(code="G03", status_code=400, detail="Invalid color value")
        
    except Exception as e:
        raise CustomHTTPException("G00", 500, f"Error applying makeup: {e}")

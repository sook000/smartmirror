from fastapi import UploadFile
from app.model_loader import sess, X, Y, Xs, detector, sp
from app.utils import (
    get_image_from_url, pil_to_numpy, align_faces, preprocess,
    postprocess, resize_with_aspect_ratio, add_padding_to_square
)
from app.exceptions import CustomHTTPException, create_response
from PIL import Image, UnidentifiedImageError
import numpy as np
import io
import base64

async def apply_makeup(inputImage: UploadFile, styleImage: str):
    # 입력 파일과 스타일 이미지 유효성 검사
    if not inputImage or not styleImage:
        raise CustomHTTPException(code="F02", status_code=400, detail="Input data missing")

    # inputImage를 읽어서 PIL 이미지로 변환
    try:
        src_pil = Image.open(io.BytesIO(await inputImage.read())).convert("RGB")
    except UnidentifiedImageError:
        raise CustomHTTPException(code="F00", status_code=400, detail="Invalid input image")

    # styleImage URL로부터 이미지 다운로드
    ref_pil = get_image_from_url(styleImage)

    # PIL 이미지를 numpy로 변환
    src_img = pil_to_numpy(src_pil)
    ref_img = pil_to_numpy(ref_pil)

    # 얼굴 정렬
    src_faces = align_faces(src_img, detector, sp)
    ref_faces = align_faces(ref_img, detector, sp)

    if len(src_faces) == 0 or len(ref_faces) == 0:
        raise CustomHTTPException(code="G00", status_code=500, detail="Face alignment failed")

    # 얼굴 이미지 전처리
    X_img = preprocess(src_faces[0])
    X_img = np.expand_dims(X_img, axis=0)
    Y_img = preprocess(ref_faces[0])
    Y_img = np.expand_dims(Y_img, axis=0)

    # 모델 실행 (AI 처리 시간 초과에 대한 예외 처리)
    try:
        output = sess.run(Xs, feed_dict={X: X_img, Y: Y_img})
    except Exception:
        raise CustomHTTPException(code="G01", status_code=500, detail="AI processing timeout")

    # 이미지 후처리
    output_img = postprocess(output[0])
    output_img_pil = Image.fromarray(output_img.astype(np.uint8))
    # 원본 비율 유지하며 리사이즈 (긴 쪽이 500)
    output_img_pil_resized = resize_with_aspect_ratio(output_img_pil, 500)
    # 패딩 추가
    output_img_pil = add_padding_to_square(output_img_pil_resized, 500)

    # 이미지 base64로 변환
    img_byte_arr = io.BytesIO()
    output_img_pil.save(img_byte_arr, format='JPEG')
    img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

    # 응답 반환
    return create_response("A00", {"makeupImage": img_base64}, status_code=200)
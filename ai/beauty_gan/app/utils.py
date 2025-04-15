from PIL import Image, UnidentifiedImageError
import numpy as np
import requests
import io
import dlib
from app.exceptions import CustomHTTPException

# 얼굴 정렬 함수 (dlib 기반)
def align_faces(img, detector, sp):
    dets = detector(img, 1)
    objs = dlib.full_object_detections()
    for detection in dets:
        s = sp(img, detection)
        objs.append(s)
    faces = dlib.get_face_chips(img, objs, size=256, padding=0.35)
    return faces

# 이미지 정규화 전처리
def preprocess(img):
    return img / 127.5 - 1.0

# 이미지 후처리 (정규화 복원)
def postprocess(img):
    return (img + 1.0) * 127.5

# PIL 이미지를 numpy 배열로 변환
def pil_to_numpy(pil_img):
    return np.array(pil_img)

# 이미지 URL로부터 이미지를 가져오는 함수
def get_image_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        img = Image.open(io.BytesIO(response.content)).convert("RGB")
        return img
    except requests.exceptions.RequestException:
        raise CustomHTTPException(code="G02", status_code=500, detail="Failed to fetch style image")
    except UnidentifiedImageError:
        raise CustomHTTPException(code="G00", status_code=500, detail="Invalid image format or corrupted image")

# 종횡비를 유지하면서 이미지 리사이즈
def resize_with_aspect_ratio(image, target_size):
    # 원본 이미지 크기 가져오기
    width, height = image.size
    # 비율
    aspect_ratio = width / height

    if width > height:
        new_width = target_size
        new_height = int(target_size / aspect_ratio)
    else:
        new_height = target_size
        new_width = int(target_size * aspect_ratio)
    return image.resize((new_width, new_height), Image.ANTIALIAS)

# 정사각형 패딩 추가 (배경 흰색)
def add_padding_to_square(image, target_size, fill_color=(255, 255, 255)):
    width, height = image.size
    new_image = Image.new("RGB", (target_size, target_size), fill_color)
    new_image.paste(image, ((target_size - width) // 2, (target_size - height) // 2))
    return new_image

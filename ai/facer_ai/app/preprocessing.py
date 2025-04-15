import dlib, cv2
from .exceptions import CustomHTTPException

# 얼굴 탐지기 초기화
detector = dlib.get_frontal_face_detector()

# 이미지 리사이즈 함수
def resize_image(image, target_size=(500, 500)):
    return cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)

# 얼굴 탐지 후 가장 큰 얼굴 크롭
def detect_and_crop_largest_face(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    dets = detector(gray, 1) # 얼굴 탐지
    if not dets:
        raise CustomHTTPException("G05", 400, "No face detected")

    # 가장 큰 얼굴 탐지
    largest = max(dets, key=lambda r: r.width() * r.height())
    
    # 얼굴 크기 조절: 크기가 너무 작으면 무시
    if largest.width() * largest.height() < 1000:
        raise CustomHTTPException("G05", 400, "Detected face is too small")

    # 얼굴 주변으로 이미지 자르기
    margin = 0.6 # 얼굴 주위로 60% 여유 공간을 둠
    x1 = max(0, int(largest.left() - margin * largest.width()))
    y1 = max(0, int(largest.top() - margin * largest.height()))
    x2 = min(image.shape[1], int(largest.right() + margin * largest.width()))
    y2 = min(image.shape[0], int(largest.bottom() + margin * largest.height()))

    cropped = image[y1:y2, x1:x2]
    
    # 크롭된 이미지를 리사이즈
    resized = resize_image(cropped, (500, 500))

    # 크롭된 이미지와 크롭 위치(x, y, width, height)
    return resized, (x1, y1, x2 - x1, y2 - y1)

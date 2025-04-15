import os, json, numpy as np, torch, facer
from .cache import segmentation_cache_dir
import time

# CUDA 사용 가능 여부 확인(CUDA 설정)
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# 얼굴 세그멘테이션 수행 함수
def segment_face(image, image_hash, crop_info):
    image_tensor = facer.hwc2bchw(torch.from_numpy(image).to(torch.float32)).to(device=device)
    face_detector = facer.face_detector('retinaface/mobilenet', device=device)
    face_parser = facer.face_parser('farl/lapa/448', device=device)

    with torch.inference_mode():
        faces = face_detector(image_tensor)
        faces = face_parser(image_tensor, faces)

    # 세그멘테이션 맵 추출
    seg_logits = faces['seg']['logits']
    seg_result = seg_logits.softmax(dim=1).argmax(dim=1).squeeze().cpu().numpy()

    # 세그멘테이션 결과를 캐시에 저장
    save_segmentation_result(image_hash, seg_result, crop_info)
    return seg_result

# 세그멘테이션 결과 저장(이미지 파일, 타임 스탬프, 크롭 정보)
def save_segmentation_result(image_hash, seg_result, crop_info):
    # 세그멘테이션 결과 저장
    np.save(os.path.join(segmentation_cache_dir, f"{image_hash}_seg.npy"), seg_result)
    
    # 타임스탬프 저장
    with open(os.path.join(segmentation_cache_dir, f"{image_hash}_timestamp.txt"), "w") as f:
        f.write(str(time.time()))
    
    # 크롭 정보 저장
    with open(os.path.join(segmentation_cache_dir, f"{image_hash}_cropinfo.json"), "w") as f:
        json.dump(crop_info, f)

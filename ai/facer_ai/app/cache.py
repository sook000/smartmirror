import os, shutil, time
from threading import Thread

# 캐시 디렉토리 경로 설정
segmentation_cache_dir = "./segmentation_cache/"
# 캐시 유지 시간 (초 단위, 30분 = 1800초)
CACHE_EXPIRATION_TIME = 5 * 60

# 캐시 디렉토리 없을 경우 생성
if not os.path.exists(segmentation_cache_dir):
    os.makedirs(segmentation_cache_dir)

# SSD 용량 확인 후 필요한 경우 오래된 파일 삭제
def check_ssd_usage():
    total, used, free = shutil.disk_usage(segmentation_cache_dir)
    
    total_gb = total / (1024 * 1024 * 1024)
    used_gb = used / (1024 * 1024 * 1024)
    free_gb = free / (1024 * 1024 * 1024)
    
    # print(f"Total: {total_gb:.2f} GB, Used: {used_gb:.2f} GB, Free: {free_gb:.2f} GB")
    
    # 만약 사용량이 90% 이상이면 가장 오래된 파일부터 삭제
    if used / total > 0.9:
        remove_oldest_files()

# 가장 오래된 파일 삭제 함수       
def remove_oldest_files():
    files = [os.path.join(segmentation_cache_dir, f) for f in os.listdir(segmentation_cache_dir)]
    files.sort(key=os.path.getmtime) # 파일 생성 날짜 기준으로 정렬(오래된 파일부터)
    for file in files:
        os.remove(file)
        break

# 캐시 파일 만료 여부 확인
def is_expired(timestamp_path):
    with open(timestamp_path, "r") as f:
        timestamp = float(f.read())
    return (time.time() - timestamp) > CACHE_EXPIRATION_TIME

# 만료된 파일 삭제
def remove_expired_files():
    for file_name in os.listdir(segmentation_cache_dir):
        if file_name.endswith("_timestamp.txt"):

            timestamp_path = os.path.join(segmentation_cache_dir, file_name)
            if not is_expired(timestamp_path):
                continue  # 만료되지 않았다면 삭제하지 않음
            
            image_hash = file_name.split("_timestamp.txt")[0]
            paths = [f"{image_hash}_seg.npy", f"{image_hash}_cropinfo.json", file_name]
            for p in paths:
                fp = os.path.join(segmentation_cache_dir, p)
                if os.path.exists(fp): os.remove(fp)

# 주기적으로 만료된 파일 및 용량 체크
def cleanup_cache():
    while True:
        remove_expired_files() # 만료된 파일 삭제
        check_ssd_usage()      # SSD 용량 체크
        time.sleep(60)         # 1분마다 실행

# 백그라운드 쓰레드로 캐시 정리 함수 실행
def start_cache_cleanup_thread():
    Thread(target=cleanup_cache, daemon=True).start()

import numpy as np, cv2

# 세그멘테이션 결과를 이용한 메이크업 색상 적용 함수
def apply_color_changes(image_np, seg_result, eyebrowColor=None, skinColor=None, lipColor=None, lipMode=None):
    # 피부 및 코 색상 변경(클래스 1은 피부, 클래스 6은 코)
    for cls, color in [(1, skinColor), (6, skinColor)]: 
        if color is not None:
            mask = seg_result == cls

            if mask.any():
                # 기존과 새로운 색 혼합
                alpha = 0.85
                color_expanded = np.tile(color, (mask.sum(), 1))
                image_np[mask] = cv2.addWeighted(image_np[mask].astype(np.float32), alpha, color_expanded.astype(np.float32), 1 - alpha, 0)

    # 눈썹 색상 변경(클래스2는 왼쪽 눈썹, 클래스 3은 오른쪽 눈썹썹)
    for cls in [2, 3]:
        if eyebrowColor is not None:
            mask = seg_result == cls
            if mask.any():
                alpha = 0.82
                color_expanded = np.tile(eyebrowColor, (mask.sum(), 1))
                image_np[mask] = cv2.addWeighted(image_np[mask].astype(np.float32), alpha, color_expanded.astype(np.float32), 1 - alpha, 0)

    # 입술 색상 변경 (풀립 또는 그라데이션)
    if lipColor is not None and lipMode:
        mask = (seg_result == 7) | (seg_result == 9) #(클래스 7은 윗입술, 클래스 8은 아랫입술 )
        if mask.any():
            # 풀립 색상 변경 (기존 색과 새로운 색을 혼합)
            if lipMode == "full":
                alpha = 0.6
                color_expanded = np.tile(lipColor, (mask.sum(), 1))
                image_np[mask] = cv2.addWeighted(image_np[mask].astype(np.float32), alpha, color_expanded.astype(np.float32), 1 - alpha, 0)
            # 그라데이션 립 효과 적용
            elif lipMode == "gradient":
                dist = cv2.distanceTransform(mask.astype(np.uint8), cv2.DIST_L2, 5)
                grad = cv2.normalize(dist, None, 0, 1, cv2.NORM_MINMAX)
                for i in range(3):
                    image_np[:, :, i] = image_np[:, :, i] * (1 - grad) + lipColor[i] * grad
    return image_np

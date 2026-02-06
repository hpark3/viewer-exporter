import os
import cv2
import numpy as np
from pdf2image import convert_from_path
from dotenv import load_dotenv

load_dotenv()

POPPLER_BIN_PATH = r"C:\poppler\Library\bin"
RAW_SAVE_DIR = os.getenv("SAVE_DIR")
SAVE_DIR = os.path.normpath(RAW_SAVE_DIR)
PDF_FILE_NAME = os.getenv("PDF_FILE_NAME", "final_document_complete.pdf")
PDF_PATH = os.path.join(SAVE_DIR, PDF_FILE_NAME)

def is_loading_error(img_array):
    """
    개선된 로직: 회색 박스를 검출한 후, 내부의 균일도(Standard Deviation)를 분석합니다.
    """
    h, w, _ = img_array.shape
    # 텍스트 간섭을 줄이기 위해 전체 화면에서 분석하되, 너무 끝부분은 제외
    cz = img_array[h//10:9*h//10, w//10:9*w//10]
    
    # 1. 캔바 로딩색(#EBEBEB) 마스크 생성 (범위를 약간 넓혀 노이즈 대응)
    gray_low = np.array([230, 230, 230])
    gray_high = np.array([242, 242, 242])
    mask = cv2.inRange(cz, gray_low, gray_high)
    
    # 2. 회색 덩어리(Contours) 찾기
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for cnt in contours:
        x, y, bw, bh = cv2.boundingRect(cnt)
        
        # 너무 작은 점들은 무시 (최소 80픽셀 이상)
        if bw < 80 or bh < 30:
            continue
            
        # 해당 회색 영역만 잘라내서 내부 분석
        roi = cz[y:y+bh, x:x+bw]
        
        # 3. 내부 균일도 분석 (로딩 박스는 거의 완벽한 단색임)
        # 실제 로딩 박스는 표준편차가 1 미만으로 매우 낮음
        std_dev = np.std(roi)
        
        # 4. 내부 색상 비중 (박스 안에 회색이 얼마나 꽉 차있는가)
        roi_mask = mask[y:y+bh, x:x+bw]
        gray_in_box_ratio = np.sum(roi_mask > 0) / (bw * bh)
        
        # [판정 조건]
        # - 박스 내 회색 비중이 95% 이상이고
        # - 내부 색상 변화(std)가 매우 적으며 (글자나 그림이 없음)
        # - 면적이 어느 정도 되는 경우
        if gray_in_box_ratio > 0.95 and std_dev < 3.0:
            return True, gray_in_box_ratio, std_dev

    return False, 0, 0

def find_error_pages(pdf_path):
    if not os.path.exists(pdf_path): return
    print(f"🔍 [{PDF_FILE_NAME}] 균일도 기반 정밀 스캔 시작...")
    
    # 정밀한 분석을 위해 DPI를 100으로 유지
    pages = convert_from_path(pdf_path, dpi=100, poppler_path=POPPLER_BIN_PATH)
    error_pages = []

    for i, page in enumerate(pages):
        page_num = i + 1
        img_array = np.array(page)
        is_error, ratio, std = is_loading_error(img_array)

        if is_error:
            print(f" 🚩 [Page {page_num}] 오류 감지 (균일도:{std:.2f})")
            error_pages.append(page_num)

    print("-" * 30)
    print(f"📍 최종 리스트: {error_pages}")

if __name__ == "__main__":
    find_error_pages(PDF_PATH)
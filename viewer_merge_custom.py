import os
import re
from PIL import Image
from pypdf import PdfWriter
from dotenv import load_dotenv

load_dotenv()
RAW_SAVE_DIR = os.getenv("SAVE_DIR")
SAVE_DIR = os.path.normpath(RAW_SAVE_DIR)
TEMP_DIR = os.path.join(SAVE_DIR, "temp")

def get_unique_filename(directory, base_filename):
    name, ext = os.path.splitext(base_filename)
    counter = 1
    final_path = os.path.join(directory, base_filename)
    while os.path.exists(final_path):
        new_filename = f"{name} ({counter}){ext}"
        final_path = os.path.join(directory, new_filename)
        counter += 1
    return final_path

def merge_with_custom_captures():
    if not os.path.exists(TEMP_DIR):
        print(f"❌ temp 폴더를 찾을 수 없습니다: {TEMP_DIR}")
        return

    # 결과 파일 저장 경로 (자동 넘버링 포함)
    output_path = get_unique_filename(SAVE_DIR, "final_document_fixed.pdf")
    pdf_writer = PdfWriter()

    # 1. temp 폴더 내의 모든 PDF 파일을 수집
    all_files = os.listdir(TEMP_DIR)
    
    # [수정된 패턴] 타임스탬프 유무와 상관없이 'temp_page_번호.pdf' 형식을 찾습니다.
    # ^temp_page_(\d+)\.pdf$ : 'temp_page_번호.pdf'와 정확히 일치하는 경우
    # (?:.*_)?(\d+)\.pdf$ : 앞에 다른 숫자가 더 붙어 있어도 끝의 페이지 번호만 추출
    pdf_pattern = re.compile(r"temp_page_(?:.*_)?(\d+)\.pdf$")
    
    pdf_map = {}
    for f in all_files:
        match = pdf_pattern.search(f)
        if match:
            page_num = int(match.group(1))
            pdf_map[page_num] = os.path.join(TEMP_DIR, f)

    if not pdf_map:
        print(f"⚠️ 병합할 PDF 조각이 없습니다. (확인된 경로: {TEMP_DIR})")
        print(f"📂 현재 폴더 내 파일 예시: {all_files[:5]}")
        return

    # 페이지 번호 순으로 정렬
    sorted_pages = sorted(pdf_map.keys())
    print(f"🪄 총 {len(sorted_pages)}개 페이지 병합 및 교체 시작...")

    for i in sorted_pages:
        # PNG 파일 확인 (temp_page_번호.png)
        custom_png_path = os.path.join(TEMP_DIR, f"temp_page_{i}.png")
        
        if os.path.exists(custom_png_path):
            print(f" > [{i}페이지] 📸 수동 PNG로 교체 중...")
            img = Image.open(custom_png_path).convert("RGB")
            temp_img_pdf = os.path.join(TEMP_DIR, f"temp_converted_{i}.pdf")
            # PDF 변환 및 라이터 추가
            img.save(temp_img_pdf, "PDF", resolution=100.0)
            pdf_writer.append(temp_img_pdf)
            os.remove(temp_img_pdf)
        else:
            print(f" > [{i}페이지] 📝 기존 PDF 조각 사용...")
            pdf_writer.append(pdf_map[i])

    # 최종 결과물 저장
    with open(output_path, "wb") as f:
        pdf_writer.write(f)

    print("-" * 30)
    print(f"✨ 교체 완료! 최종 파일: {output_path}")

if __name__ == "__main__":
    merge_with_custom_captures()
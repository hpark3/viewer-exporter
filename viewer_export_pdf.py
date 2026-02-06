from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from pypdf import PdfWriter
import time
import os
import re

# .env 파일 로드
load_dotenv()

TARGET_URL = os.getenv("TARGET_URL")
RAW_SAVE_DIR = os.getenv("SAVE_DIR")
SAVE_DIR = os.path.normpath(RAW_SAVE_DIR)
# 임시 파일을 저장할 전용 폴더 설정
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

FINAL_OUTPUT_PATH = get_unique_filename(SAVE_DIR, "final_document_complete.pdf")

def export_clean_document_pdf():
    # 저장 폴더 및 템프 폴더 생성
    if not os.path.exists(SAVE_DIR): os.makedirs(SAVE_DIR)
    if not os.path.exists(TEMP_DIR): os.makedirs(TEMP_DIR)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        print("🚀 대상 페이지 접속 중...")
        page.goto(TARGET_URL, wait_until="networkidle")
        time.sleep(10)

        # 총 페이지 수 파악
        try:
            page_text = page.locator("body").inner_text()
            match = re.search(r"(\d+)\s*/\s*(\d+)", page_text)
            total_pages = int(match.group(2)) if match else 133
            print(f"✅ 총 {total_pages}페이지 확인.")
        except:
            total_pages = 133

        pdf_writer = PdfWriter()

        # 추출 루프 시작
        for i in range(1, total_pages + 1):
            # 1. 실시간 프로세스 출력
            print(f" > [{i}/{total_pages}] 페이지 처리 중...")

            # 2. 서버 과부하 방지 (20페이지마다 10초 휴식)
            if i > 1 and i % 20 == 0:
                print(f"☕ 서버 보호를 위해 잠시 멈춥니다. (10초 대기 후 재개)")
                time.sleep(10)

            # 3. UI 숨기기
            page.evaluate("""() => {
                const selectors = ['header', 'footer', '[role="toolbar"]', 'button', 'div[class*="Header"]', '.notion-topbar', '.UiPresenter_presenter_controls'];
                selectors.forEach(s => {
                    document.querySelectorAll(s).forEach(el => el.style.display = 'none');
                });
            }""")

            # 4. 고화질 렌더링 대기
            time.sleep(3.0)

            # 5. 임시 PDF 파일 생성 (타임스탬프 없이 페이지 번호로만 고정)
            # 나중에 viewer_merge_custom.py에서 temp_page_번호.png와 매칭하기 위함입니다.
            temp_pdf_name = f"temp_page_{i}.pdf"
            temp_pdf_path = os.path.join(TEMP_DIR, temp_pdf_name)
            
            # 기존 동일 번호 파일이 있으면 삭제하여 최신화
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)
            
            # PDF 저장
            page.pdf(path=temp_pdf_path, width="1920px", height="1080px", print_background=True)
            pdf_writer.append(temp_pdf_path)

            # 6. 다음 페이지로 이동
            if i < total_pages:
                page.keyboard.press("ArrowRight")
                # 페이지 전환 후 서버 안정화 대기 시간을 2.5초로 넉넉히 둡니다.
                time.sleep(2.5)

        # 7. 최종 병합 파일 생성
        print(f"🔗 초기 병합 파일 생성 중: {FINAL_OUTPUT_PATH}")
        with open(FINAL_OUTPUT_PATH, "wb") as f:
            pdf_writer.write(f)

        browser.close()
        print(f"✨ 완료! 개별 PDF 조각들은 '{TEMP_DIR}' 폴더에 보관되었습니다.")

if __name__ == "__main__":
    export_clean_document_pdf()
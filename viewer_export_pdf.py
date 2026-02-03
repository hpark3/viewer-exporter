from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from pypdf import PdfWriter
import time
import os
import re

# .env 파일 로드
load_dotenv()

# =========================
# 설정
# =========================
TARGET_URL = os.getenv("TARGET_URL")
RAW_SAVE_DIR = os.getenv("SAVE_DIR")

SAVE_DIR = os.path.normpath(RAW_SAVE_DIR)
FINAL_OUTPUT_PATH = os.path.join(SAVE_DIR, "final_document_complete.pdf")

def export_clean_document_pdf():
    if not os.path.exists(SAVE_DIR): 
        os.makedirs(SAVE_DIR)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        print("🚀 대상 페이지 접속 중...")
        page.goto(TARGET_URL, wait_until="commit")
        time.sleep(15) # 전체 콘텐츠 로딩 대기

        # [핵심 추가] 총 페이지 수 자동 파악 로직
        print("🔍 총 페이지 수 파악 중...")
        try:
            # 페이지 하단 등에 있는 '1 / 133' 형태의 텍스트를 찾습니다.
            # 캔바 뷰어의 일반적인 텍스트 패턴을 타겟팅합니다.
            page_text = page.locator("body").inner_text()
            # "현재페이지 / 총페이지" 패턴 추출 (예: 1 / 133)
            match = re.search(r"(\d+)\s*/\s*(\d+)", page_text)
            
            if match:
                total_pages = int(match.group(2))
                print(f"✅ 총 {total_pages}페이지를 확인했습니다.")
            else:
                # 패턴을 못 찾을 경우 사용자에게 물어보거나 기본값 설정
                total_pages = 133 # 패턴 인식 실패 시 기본값 (직접 입력 가능)
                print(f"⚠️ 페이지 번호를 찾지 못해 기본값({total_pages})으로 진행합니다.")
        except Exception as e:
            total_pages = 133 
            print(f"⚠️ 오류 발생으로 기본값({total_pages})으로 진행합니다: {e}")

        pdf_writer = PdfWriter()
        temp_pdf_list = []

        print(f"🪄 인터페이스 정리 및 {total_pages}개 페이지 추출 시작...")
        
        for i in range(1, total_pages + 1):
            print(f" > [{i}/{total_pages}] 페이지 처리 중...")
            
            # UI 숨기기 및 배경 정리
            page.evaluate("""
                () => {
                    const selectors = [
                        'header', 'footer', '[role="toolbar"]', 'button',
                        'div[class*="Header"]', 'div[class*="Footer"]', 
                        'div[class*="Gradient"]', 'div[class*="Overlay"]',
                        '.notion-topbar', '.UiPresenter_presenter_controls'
                    ];
                    selectors.forEach(s => {
                        document.querySelectorAll(s).forEach(el => el.style.display = 'none');
                    });
                    document.body.style.background = "white";
                    const rootElement = document.querySelector('#root') || document.body;
                    rootElement.style.background = "white";
                    rootElement.style.backgroundImage = "none";
                }
            """)
            time.sleep(1)

            temp_pdf_path = os.path.join(SAVE_DIR, f"temp_page_{i}.pdf")
            page.pdf(
                path=temp_pdf_path,
                width="1920px", height="1080px",
                print_background=True, display_header_footer=False
            )
            
            pdf_writer.append(temp_pdf_path)
            temp_pdf_list.append(temp_pdf_path)

            if i < total_pages:
                page.keyboard.press("ArrowRight")
                time.sleep(1.2) # 페이지 전환 대기

        print("🔗 파일 병합 중...")
        with open(FINAL_OUTPUT_PATH, "wb") as f:
            pdf_writer.write(f)

        for temp_file in temp_pdf_list:
            if os.path.exists(temp_file): os.remove(temp_file)

        browser.close()
        print(f"✨ 완료! 저장 경로: {FINAL_OUTPUT_PATH}")

if __name__ == "__main__":
    export_clean_document_pdf()
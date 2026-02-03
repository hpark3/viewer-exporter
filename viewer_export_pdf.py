from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from pypdf import PdfWriter
import time
import os

# .env 파일 로드
load_dotenv()

# 설정
# 환경 변수에서 가져오기 (없을 경우를 대비해 기본값 설정 가능)
URL = os.getenv("CANVA_URL")
SAVE_DIR = os.getenv("SAVE_DIR")
FINAL_PATH = os.path.join(SAVE_DIR, "canva_final_complete_clean.pdf")

def export_full_clean_pdf():
    if not os.path.exists(SAVE_DIR): os.makedirs(SAVE_DIR)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        print("🚀 페이지 접속 중...")
        page.goto(URL, wait_until="commit")
        time.sleep(15) # 전체 로딩 대기

        pdf_writer = PdfWriter()
        temp_files = []

        print("🪄 UI 제거 및 페이지별 인쇄 시작...")
        
        for i in range(1, 18):
            print(f" > [{i}/17] 페이지 처리 중...")
            
            # [핵심] 매 페이지마다 상/하단 UI 요소를 강제로 숨기고 배경을 흰색으로 고정
            page.evaluate("""
                () => {
                    const selectors = [
                        'header', 'footer', '.notion-topbar', '[role="toolbar"]', 
                        'button', '.UiPresenter_presenter_controls', 'div[class*="Header"]',
                        'div[class*="Footer"]', 'div[class*="Gradient"]', 'div[class*="Overlay"]'
                    ];
                    selectors.forEach(s => {
                        document.querySelectorAll(s).forEach(el => el.style.display = 'none');
                    });
                    // 전체 배경 및 그라데이션 제거
                    document.body.style.background = "white";
                    const root = document.querySelector('#root') || document.body;
                    root.style.background = "white";
                    root.style.backgroundImage = "none";
                }
            """)
            time.sleep(1)

            # 각 페이지를 임시 PDF로 인쇄
            temp_pdf = os.path.join(SAVE_DIR, f"temp_{i}.pdf")
            page.pdf(
                path=temp_pdf,
                width="1920px", height="1080px",
                print_background=True, display_header_footer=False
            )
            
            # PDF 병합 리스트에 추가
            pdf_writer.append(temp_pdf)
            temp_files.append(temp_pdf)

            # 다음 페이지로 이동
            if i < 17:
                page.keyboard.press("ArrowRight")
                time.sleep(1.5) # 페이지 전환 및 렌더링 대기

        # 모든 페이지 합치기
        print("🔗 PDF 병합 중...")
        with open(FINAL_PATH, "wb") as f:
            pdf_writer.write(f)

        # 임시 파일 삭제
        for f in temp_files:
            if os.path.exists(f): os.remove(f)

        browser.close()
        print(f"✨ 완료! 상/하단 로고가 없는 17페이지 PDF가 저장되었습니다: {FINAL_PATH}")

if __name__ == "__main__":
    export_full_clean_pdf()
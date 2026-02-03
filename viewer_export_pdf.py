from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from pypdf import PdfWriter
import time
import os

# .env 파일 로드
load_dotenv()

# =========================
# 설정
# =========================
# 환경 변수 .env에서 읽어오기
TARGET_URL = os.getenv("TARGET_URL")
RAW_SAVE_DIR = os.getenv("SAVE_DIR")

# 윈도우 경로 정규화 및 최종 파일 경로 설정
SAVE_DIR = os.path.normpath(RAW_SAVE_DIR)
FINAL_OUTPUT_PATH = os.path.join(SAVE_DIR, "final_document_complete.pdf")

def export_clean_document_pdf():
    # 저장 폴더가 없으면 생성
    if not os.path.exists(SAVE_DIR): 
        os.makedirs(SAVE_DIR)
    
    with sync_playwright() as p:
        # 브라우저 실행 및 컨텍스트 설정
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        print("🚀 대상 페이지 접속 중...")
        page.goto(TARGET_URL, wait_until="commit")
        time.sleep(15) # 전체 콘텐츠 로딩 대기

        pdf_writer = PdfWriter()
        temp_pdf_list = []

        print("🪄 인터페이스 정리 및 페이지별 추출 시작...")
        
        # 총 페이지 수 설정 (예: 17페이지)
        total_pages = 17
        
        for i in range(1, total_pages + 1):
            print(f" > [{i}/{total_pages}] 페이지 처리 중...")
            
            # 매 페이지마다 불필요한 UI 요소를 숨기고 배경을 흰색으로 고정하는 스크립트
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

                    // 배경색 강제 고정 및 그래픽 효과 제거
                    document.body.style.background = "white";
                    const rootElement = document.querySelector('#root') || document.body;
                    rootElement.style.background = "white";
                    rootElement.style.backgroundImage = "none";
                }
            """)
            time.sleep(1)

            # 현재 슬라이드를 임시 PDF 파일로 저장
            temp_pdf_path = os.path.join(SAVE_DIR, f"temp_page_{i}.pdf")
            page.pdf(
                path=temp_pdf_path,
                width="1920px", 
                height="1080px",
                print_background=True, 
                display_header_footer=False
            )
            
            # 병합 리스트에 추가
            pdf_writer.append(temp_pdf_path)
            temp_pdf_list.append(temp_pdf_path)

            # 마지막 페이지가 아니면 다음으로 이동
            if i < total_pages:
                page.keyboard.press("ArrowRight")
                time.sleep(1.5) # 전환 애니메이션 대기

        # 모든 PDF 조각 병합
        print("🔗 파일 병합 및 최적화 중...")
        with open(FINAL_OUTPUT_PATH, "wb") as f:
            pdf_writer.write(f)

        # 사용이 끝난 임시 파일 삭제
        for temp_file in temp_pdf_list:
            if os.path.exists(temp_file): 
                os.remove(temp_file)

        browser.close()
        print(f"✨ 완료! 깔끔한 PDF 문서가 저장되었습니다: {FINAL_OUTPUT_PATH}")

if __name__ == "__main__":
    export_clean_document_pdf()
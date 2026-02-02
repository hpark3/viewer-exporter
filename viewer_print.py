from playwright.sync_api import sync_playwright
import time
import os

# 설정
URL = "https://www.canva.com/design/DAG_woyLVDE/ZobIVpU7OzTOu1Y6j5lpEw/view?utm_content=DAG_woyLVDE&utm_campaign=designshare&utm_medium=link2&utm_source=uniquelinks&utlId=h5f5b581b96#1"
SAVE_PATH = r"C:\Users\hyera\Downloads\SeSAC(2026) - 데이터분석\Excel\viewer_docs\canva_final_clean.pdf"

def export_clean_pdf():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # 고해상도 설정을 위해 디바이스 스케일 팩터 추가
        context = browser.new_context(viewport={"width": 1920, "height": 1080}, device_scale_factor=2)
        page = context.new_page()

        # 1. 타임아웃 제한 해제 (무제한 대기 방지 위해 120초 설정)
        page.set_default_timeout(120000) 

        print("🚀 페이지 접속 중 (최대 2분 대기)...")
        try:
            # networkidle 대신 commit까지만 기다리고 뒤에서 수동 대기
            page.goto(URL, wait_until="commit")
            print("⏳ 콘텐츠가 로드되기를 기다리는 중 (20초)...")
            time.sleep(20) 
        except Exception as e:
            print(f"⚠️ 로딩 중 경고 발생: {e}")

        # [핵심 1] 레이아웃 정리 (불필요한 UI 제거)
        print("🪄 레이아웃 정리 중 (친구분 파일처럼 깔끔하게)...")
        page.evaluate("""
            () => {
                const style = document.createElement('style');
                style.innerHTML = `
                    /* 상단바, 하단바, 툴바, 로고 등 싹 제거 */
                    .notion-topbar, footer, [role="toolbar"], .UiPresenter_presenter_controls, 
                    div[class*="UiPresenter_controls"], div[class*="StandardLayout_footer"] {
                        display: none !important;
                    }
                    /* 배경을 흰색으로 고정하고 그라데이션 제거 */
                    body, .root, div[class*="UiPresenter"], div[class*="StandardLayout"] {
                        background: white !important;
                        background-image: none !important;
                    }
                    /* 인쇄 시 여백 및 크기 고정 */
                    @page { margin: 0; size: 1920px 1080px; }
                `;
                document.head.appendChild(style);
            }
        """)

        # [핵심 2] 17페이지 데이터 강제 로드 (ArrowRight로 끝까지 훑기)
        print("📜 텍스트 데이터 로딩을 위해 전 페이지 스캔 중...")
        for i in range(1, 18):
            page.keyboard.press("ArrowRight")
            time.sleep(0.8) # 각 슬라이드 로딩 시간 확보
            if i % 5 == 0: print(f" > {i}/17 페이지 스캔 완료")
        
        # 다시 1페이지로 복귀
        for _ in range(17):
            page.keyboard.press("ArrowLeft")
            
        time.sleep(2) # 최종 렌더링 대기

        print(f"📄 PDF 생성 시작: {SAVE_PATH}")
        
        # [핵심 3] PDF 인쇄
        page.pdf(
            path=SAVE_PATH,
            width="1920px",
            height="1080px",
            print_background=True,
            display_header_footer=False,
            prefer_css_page_size=True
        )

        browser.close()
        print(f"✨ 완료! '{SAVE_PATH}'에서 결과물을 확인하세요.")

if __name__ == "__main__":
    export_clean_pdf()
from playwright.sync_api import sync_playwright
import time
import os

# 설정
URL = "https://www.canva.com/design/DAG_woyLVDE/ZobIVpU7OzTOu1Y6j5lpEw/view?utm_content=DAG_woyLVDE&utm_campaign=designshare&utm_medium=link2&utm_source=uniquelinks&utlId=h5f5b581b96#1"
SAVE_PATH = r"C:\Users\hyera\Downloads\SeSAC(2026) - 데이터분석\Excel\viewer_docs\canva_final_perfect.pdf"

def export_perfect_pdf():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # 실제 캔바 슬라이드 비율에 최적화된 뷰포트 설정
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        print("🚀 페이지 접속 중...")
        page.goto(URL, wait_until="commit")
        
        # 캔바 엔진이 완전히 올라올 때까지 충분히 대기
        print("⏳ 캔바 엔진 로딩 대기 (20초)...")
        time.sleep(20)

        # [수정 포인트 1] 상단 UI 및 로고, 그라데이션 강제 제거 스크립트
        print("🪄 상단 UI 및 로고 제거 중...")
        page.evaluate("""
            () => {
                const style = document.createElement('style');
                style.innerHTML = `
                    /* 상단 검정 헤더와 버튼들 제거 */
                    header, .notion-topbar, .UiPresenter_presenter_controls, 
                    .StandardLayout_header, div[class*="Header"], 
                    button[class*="Share"], .CreateWithCanvaButton {
                        display: none !important;
                    }
                    /* 상단 검정 그라데이션 강제 제거 */
                    div[class*="Gradient"], div[class*="Overlay"] {
                        background: transparent !important;
                        display: none !important;
                    }
                    /* 전체 배경을 흰색으로 강제 고정 */
                    body, .root, #root, .StandardLayout_container, 
                    div[class*="UiPresenter"], div[class*="StandardLayout"] {
                        background: white !important;
                        background-image: none !important;
                    }
                    /* 인쇄 시 슬라이드 영역만 꽉 차게 설정 */
                    @page { margin: 0; size: 1920px 1080px; }
                    .StandardLayout_container { padding: 0 !important; margin: 0 !important; }
                `;
                document.head.appendChild(style);
            }
        """)

        # [수정 포인트 2] 17페이지 전체를 인쇄 엔진에 인식시키기 위한 강제 순회
        print("📜 17페이지 전체 데이터 강제 활성화 중...")
        for i in range(1, 18):
            page.keyboard.press("ArrowRight")
            time.sleep(1.0) # 페이지마다 데이터가 렌더링될 시간 확보
            if i % 5 == 0: print(f" > {i}/17 페이지 로드 완료")
        
        # 인쇄 직전 다시 1페이지로 복귀 (인쇄 엔진은 첫 위치부터 끝까지를 잡음)
        for _ in range(17):
            page.keyboard.press("ArrowLeft")
        time.sleep(3)

        print(f"📄 PDF 생성 중: {SAVE_PATH}")
        
        # [수정 포인트 3] 인쇄 범위 최적화
        page.pdf(
            path=SAVE_PATH,
            width="1920px",
            height="1080px",
            print_background=True,
            display_header_footer=False,
            prefer_css_page_size=True,
            scale=1.0 # 여백 없이 꽉 차게
        )

        browser.close()
        print(f"✨ 추출 완료! 상단 로고까지 제거된 17페이지 PDF가 생성되었습니다.")

if __name__ == "__main__":
    export_perfect_pdf()
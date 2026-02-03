from playwright.sync_api import sync_playwright
from PIL import Image
import time
import os
from datetime import datetime

# =========================
# 설정
# =========================
# URL = "https://www.canva.com/design/XXXX/view"  # Canva viewer URL
URL = "https://www.canva.com/design/DAG_woyLVDE/ZobIVpU7OzTOu1Y6j5lpEw/view?utm_content=DAG_woyLVDE&utm_campaign=designshare&utm_medium=link2&utm_source=uniquelinks&utlId=h5f5b581b96#1"

SAVE_DIR = r"C:\Users\hyera\Downloads\SeSAC(2026) - 데이터분석\Excel\viewer_docs"
os.makedirs(SAVE_DIR, exist_ok=True)

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M")
PDF_PATH = os.path.join(SAVE_DIR, f"canva_viewer_{TIMESTAMP}.pdf")

# =========================
# 1. 페이지 넘기며 캡처
# =========================
def capture_pages():
    screenshots = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2
        )
        page = context.new_page()
        page.goto(URL, wait_until="networkidle")
        time.sleep(3)

        page_num = 1

        while True:
            img_path = os.path.join(
                SAVE_DIR, f"page_{page_num:02d}.png"
            )

            page.screenshot(path=img_path, full_page=False)
            screenshots.append(img_path)
            print(f"📸 캡처 완료: {img_path}")

            # 다음 페이지 (키보드 방식이 가장 안정적)
            page.keyboard.press("ArrowRight")
            time.sleep(1.5)

            # 페이지 전환이 안 되면 종료
            # (마지막 페이지에서 더 이상 바뀌지 않음)
            if page_num > 1:
                prev_img = Image.open(screenshots[-2])
                curr_img = Image.open(screenshots[-1])

                if list(prev_img.getdata()) == list(curr_img.getdata()):
                    os.remove(img_path)
                    screenshots.pop()
                    break

            page_num += 1

        browser.close()

    return screenshots

# =========================
# 2. PNG → PDF 병합
# =========================
def images_to_pdf(images, pdf_path):
    pil_images = [Image.open(img).convert("RGB") for img in images]

    pil_images[0].save(
        pdf_path,
        save_all=True,
        append_images=pil_images[1:]
    )

    print(f"\n✅ PDF 생성 완료: {pdf_path}")

# =========================
# 실행
# =========================
if __name__ == "__main__":
    imgs = capture_pages()
    images_to_pdf(imgs, PDF_PATH)





# # 이 코드는 슬라이드를 하나씩 넘기며 temp_page_1.png, temp_page_2.png 등으로 저장한 뒤 마지막에 PDF로 합칩니다.

# from playwright.sync_api import sync_playwright
# import time
# import os
# import img2pdf

# # 설정
# URL = "https://www.canva.com/design/DAG_woyLVDE/ZobIVpU7OzTOu1Y6j5lpEw/view?utm_content=DAG_woyLVDE&utm_campaign=designshare&utm_medium=link2&utm_source=uniquelinks&utlId=h5f5b581b96#1"
# save_dir = r"C:\Users\hyera\Downloads\SeSAC(2026) - 데이터분석\Excel\viewer_docs"
# if not os.path.exists(save_dir):
#     os.makedirs(save_dir)

# final_pdf_path = os.path.join(save_dir, "canva_complete.pdf")
# total_pages = 17  # 이미지에 1/17로 표시되어 있으니 17로 설정

# with sync_playwright() as p:
#     browser = p.chromium.launch(headless=True) # 과정을 보고 싶다면 False로 변경
#     context = browser.new_context(viewport={"width": 1920, "height": 1080})
#     page = context.new_page()

#     print("페이지 접속 중...")
#     page.goto(URL, wait_until="networkidle")
#     time.sleep(5) # 초기 로딩 대기

#     image_files = []

#     for i in range(1, total_pages + 1):
#         print(f"[{i}/{total_pages}] 페이지 캡처 중...")
        
#         # 슬라이드 로딩 대기
#         time.sleep(1)
        
#         # 스크린샷 저장
#         img_path = os.path.join(save_dir, f"temp_{i}.png")
#         page.screenshot(path=img_path, full_page=False)
#         image_files.append(img_path)

#         # 마지막 페이지가 아니면 '다음' 버튼 클릭
#         if i < total_pages:
#             # 오른쪽 화살표 키 입력을 통해 다음 슬라이드로 이동
#             page.keyboard.press("ArrowRight")
#             time.sleep(0.5)

#     # 이미지들을 하나의 PDF로 합치기
#     print("PDF 병합 중...")
#     with open(final_pdf_path, "wb") as f:
#         f.write(img2pdf.convert(image_files))

#     # 임시 이미지 파일 삭제 (선택 사항)
#     for img in image_files:
#         os.remove(img)

#     browser.close()
#     print(f"✨ 모든 페이지가 포함된 PDF가 저장되었습니다: {final_pdf_path}")
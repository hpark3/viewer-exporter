import os
import re
from pypdf import PdfWriter, PdfReader
from PIL import Image
import io

WORK_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "temp")
SOURCE_PDF = os.path.join(WORK_DIR, "tableau_1.pdf")
OUTPUT_PDF = os.path.join(WORK_DIR, "tableau_1_merged.pdf")

def png_to_pdf_page(png_path, width_pt, height_pt):
    """PNG를 원본 페이지 크기에 맞춰 PDF 페이지로 변환 (PIL 사용)"""
    # 1pt = 1px at 72 DPI 기준으로 타겟 픽셀 크기 계산
    target_w = int(width_pt)
    target_h = int(height_pt)
    img = Image.open(png_path).convert("RGB")
    img = img.resize((target_w, target_h), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PDF", resolution=72)
    buf.seek(0)
    return PdfReader(buf).pages[0]

def replace_pages():
    if not os.path.exists(SOURCE_PDF):
        print(f"❌ 원본 PDF를 찾을 수 없습니다: {SOURCE_PDF}")
        return

    # temp_page_XXX.png 파일 수집
    png_pattern = re.compile(r"temp_page_(\d+)\.png$")
    replace_map = {}
    for f in os.listdir(WORK_DIR):
        m = png_pattern.match(f)
        if m:
            replace_map[int(m.group(1))] = os.path.join(WORK_DIR, f)

    if not replace_map:
        print("⚠️ 교체할 PNG 파일이 없습니다.")
        return

    print(f"📋 교체 대상 페이지: {sorted(replace_map.keys())}")

    reader = PdfReader(SOURCE_PDF)
    writer = PdfWriter()
    total = len(reader.pages)
    replaced = 0

    for i, page in enumerate(reader.pages, start=1):
        if i in replace_map:
            w = float(page.mediabox.width)
            h = float(page.mediabox.height)
            new_page = png_to_pdf_page(replace_map[i], w, h)
            writer.add_page(new_page)
            print(f"  🔄 [{i}/{total}] PNG로 교체")
            replaced += 1
        else:
            writer.add_page(page)

    with open(OUTPUT_PDF, "wb") as f:
        writer.write(f)

    print("-" * 30)
    print(f"✅ 총 {total}페이지 중 {replaced}페이지 교체 완료")
    print(f"📄 저장 경로: {OUTPUT_PDF}")

if __name__ == "__main__":
    replace_pages()

import subprocess
import sys
import time

def run_workflow():
    print("🚀 [Step 1] PDF 추출 및 초기 병합 시작...")
    # viewer_export_pdf.py 실행
    # stdout=None으로 설정하면 기존 코드의 '처리 중...' 로그를 실시간으로 볼 수 있습니다.
    process_export = subprocess.run([sys.executable, "viewer_export_pdf.py"])

    if process_export.returncode == 0:
        print("\n✅ 추출 완료! 3초 후 오류 스캔을 시작합니다...")
        time.sleep(3)
        
        print("\n🔍 [Step 2] 이미지 로딩 오류 정밀 스캔 시작...")
        # viewer_check_errors.py 실행
        subprocess.run([sys.executable, "viewer_check_errors.py"])
    else:
        print("\n❌ Step 1 추출 과정에서 문제가 발생하여 스캔을 중단합니다.")

if __name__ == "__main__":
    run_workflow()
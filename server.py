from flask import Flask, request, jsonify, Response, render_template
import subprocess, sys, os, threading, time
from pathlib import Path

app = Flask(__name__)

# --- 상태 관리 ---
log_lines = []
job_running = False
BASE_DIR = Path(__file__).parent


def append_log(line):
    log_lines.append(line)


# --- 라우트 ---

@app.route('/')
def index():
    url = request.args.get('url', '')
    return render_template('index.html', url=url)


@app.route('/status')
def status():
    return jsonify({'running': job_running})


@app.route('/run', methods=['POST'])
def run():
    global job_running, log_lines

    if job_running:
        return jsonify({'error': '이미 실행 중입니다. 완료 후 다시 시도하세요.'}), 409

    url = request.json.get('url', '').strip()
    if not url:
        return jsonify({'error': 'URL이 없습니다.'}), 400

    log_lines = []
    job_running = True

    def do_work():
        global job_running
        try:
            env = os.environ.copy()
            env['TARGET_URL'] = url
            short_url = url[:70] + '...' if len(url) > 70 else url
            append_log(f'📎 대상 URL: {short_url}')
            append_log('🚀 [Step 1] PDF 추출 시작...')

            proc = subprocess.Popen(
                [sys.executable, str(BASE_DIR / 'viewer_export_pdf.py')],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                cwd=str(BASE_DIR),
            )
            for line in proc.stdout:
                append_log(line.rstrip())
            proc.wait()

            if proc.returncode == 0:
                append_log('✅ 추출 완료! 3초 후 오류 스캔...')
                time.sleep(3)
                append_log('🔍 [Step 2] 이미지 로딩 오류 정밀 스캔...')

                proc2 = subprocess.Popen(
                    [sys.executable, str(BASE_DIR / 'viewer_check_errors.py')],
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    cwd=str(BASE_DIR),
                )
                for line in proc2.stdout:
                    append_log(line.rstrip())
                proc2.wait()
                append_log('🎉 모든 작업 완료!')
            else:
                append_log('❌ Step 1 실패. 위 로그를 확인하세요.')

        except Exception as e:
            append_log(f'💥 서버 오류: {e}')
        finally:
            job_running = False
            append_log('__DONE__')

    threading.Thread(target=do_work, daemon=True).start()
    return jsonify({'ok': True})


@app.route('/stream')
def stream():
    """Server-Sent Events로 로그를 실시간 스트리밍"""
    def generate():
        sent = 0
        while True:
            while sent < len(log_lines):
                line = log_lines[sent]
                sent += 1
                yield f'data: {line}\n\n'
                if line == '__DONE__':
                    return
            time.sleep(0.3)

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'},
    )


if __name__ == '__main__':
    print('=' * 50)
    print('🌐 Canva PDF Saver 서버 시작')
    print('📡 http://localhost:5000')
    print('=' * 50)
    print()
    print('📌 북마클릿 코드 (브라우저 주소창에 붙여넣고 북마크로 저장):')
    print()
    print("javascript:(function(){window.open('http://localhost:5000/?url='+encodeURIComponent(location.href),'CanvaSaver','width=500,height=640,menubar=no,toolbar=no,scrollbars=yes');})();")
    print()
    app.run(port=5000, debug=False, threaded=True)

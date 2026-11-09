"""
운영체제 명령어 삽입 (OS Command Injection) 실습 - 실행 가능한 뷰

PDF '시큐어 코딩(운영체제 명령어 삽입)' 슬라이드의 취약/안전 코드를 그대로
반영한다. 입력값은 직접 타이핑하는 대신 PDF 예제 목록(드롭다운)에서 선택한다.

  - 취약한 코드 : 외부 입력을 검증 없이 OS 셸로 전달 (shell=True)
  - 안전한 코드 : 특수문자 필터링 + 입력 형식 검증 + 명령/인자 리스트 분리 + 화이트리스트

※ PDF 슬라이드의 코드 원문(교과서 형태 그대로)은 oscmd/pdf_reference.py 에 보존했다.
※ 본 실습은 방어 코드 학습이 목적이며, 취약 엔드포인트는 로컬에서만 동작한다.
"""
import platform
import re
import subprocess

from django.shortcuts import render


def _ping_count_flag():
    """OS 별 ping 반복 횟수 옵션 (-n: Windows, -c: Linux/macOS)."""
    return '-n' if platform.system() == 'Windows' else '-c'


# ---------------------------------------------------------------------------
# PDF 예제 입력값 목록 (직접 타이핑 대신 드롭다운에서 선택)
# Windows(cmd.exe) 환경에서 동작하는 예제로 구성했다.
# ---------------------------------------------------------------------------
PING_EXAMPLES = [
    {'value': '8.8.8.8',
     'label': '8.8.8.8  — 정상 ping'},
    {'value': '8.8.8.8 & whoami',
     'label': '8.8.8.8 & whoami  — 1단계: 현재 계정 확인(권한)'},
    {'value': '8.8.8.8 & ipconfig',
     'label': '8.8.8.8 & ipconfig  — 네트워크 정보'},
    {'value': '8.8.8.8 & dir',
     'label': '8.8.8.8 & dir  — 현재 폴더 목록'},
    {'value': '8.8.8.8 & systeminfo',
     'label': '8.8.8.8 & systeminfo  — 시스템 정보 탈취'},
    {'value': '8.8.8.8 & echo systeminfo > test_shell.bat',
     'label': '8.8.8.8 & echo systeminfo > test_shell.bat  — 2단계: 거점 스크립트 생성'},
    {'value': '8.8.8.8 & test_shell.bat',
     'label': '8.8.8.8 & test_shell.bat  — 3단계: 거점 실행(정보 탈취)'},
]

PROGRAM_EXAMPLES = [
    {'value': 'whoami', 'label': 'whoami  — 현재 계정'},
    {'value': 'dir', 'label': 'dir  — 폴더 목록'},
    {'value': 'ipconfig', 'label': 'ipconfig  — 네트워크 정보'},
    {'value': 'systeminfo', 'label': 'systeminfo  — 시스템 정보'},
    {'value': 'calc', 'label': 'calc  — 계산기 실행(PDF 예시)'},
    {'value': 'notepad', 'label': 'notepad  — 메모장 실행(PDF 예시)'},
    {'value': 'dir & calc', 'label': 'dir & calc  — 명령 연쇄'},
]


def index(request):
    """운영체제 명령어 삽입 실습 메인 페이지."""
    return render(request, 'oscmd/index.html', {
        'is_windows': platform.system() == 'Windows',
    })


# ---------------------------------------------------------------------------
# 1) Ping a device  -  취약한 코드
# ---------------------------------------------------------------------------
def ping_vulnerable(request):
    ip = ''
    output = None
    command = None
    if request.method == 'POST':
        ip = request.POST.get('ip', '')
        # ===== 취약 지점 =====
        # 선택된 입력(ip)을 아무 검증 없이 셸 명령 문자열에 그대로 결합한다.
        # shell=True 이므로  |  ;  &  &&  등 명령 삽입 특수문자가 셸에서 해석되어
        # ping 뒤에 붙인 'whoami', 'systeminfo' 같은 2차 명령이 함께 실행된다.
        command = 'ping ' + _ping_count_flag() + ' 4 ' + ip
        completed = subprocess.run(
            command, shell=True, capture_output=True, text=True
        )
        output = (completed.stdout or '') + (completed.stderr or '')

    return render(request, 'oscmd/ping.html', {
        'safe': False,
        'title': 'Ping a device (취약한 코드)',
        'action_url': 'oscmd:ping_vulnerable',
        'examples': PING_EXAMPLES,
        'ip': ip,
        'command': command,
        'output': output,
        'error': None,
    })


# ---------------------------------------------------------------------------
# 1') Ping a device  -  안전한 코드
# ---------------------------------------------------------------------------
def ping_safe(request):
    ip = ''
    output = None
    command = None
    error = None
    if request.method == 'POST':
        ip = request.POST.get('ip', '')

        # ===== 안전 대책 1: 명령 연쇄/리다이렉트 특수문자 및 공백 제거 =====
        for word in ['|', ';', '&', ':', '>', '<', '"', '\\', '!', '`', '$',
                     '(', ')', '\n', '\r', ' ']:
            ip = ip.replace(word, '')

        # ===== 안전 대책 2: 입력값 형식 검증 (IPv4 화이트리스트 패턴) =====
        if not re.match(r'^\d{1,3}(\.\d{1,3}){3}$', ip) or \
                any(int(o) > 255 for o in ip.split('.')):
            error = '유효한 IPv4 주소 형식이 아닙니다. (명령 삽입이 차단되었습니다)'
        else:
            # ===== 안전 대책 3: shell=True 제거 + 명령/인자 리스트 분리 전달 =====
            args = ['ping', _ping_count_flag(), '4', ip]
            command = ' '.join(args)
            completed = subprocess.run(args, capture_output=True, text=True)
            output = (completed.stdout or '') + (completed.stderr or '')

    return render(request, 'oscmd/ping.html', {
        'safe': True,
        'title': 'Ping a device (안전한 코드)',
        'action_url': 'oscmd:ping_safe',
        'examples': PING_EXAMPLES,
        'ip': request.POST.get('ip', '') if request.method == 'POST' else '',
        'command': command,
        'output': output,
        'error': error,
    })


# ---------------------------------------------------------------------------
# 2) os.system 프로그램 실행  -  취약한 코드
# ---------------------------------------------------------------------------
def run_program_vulnerable(request):
    app_name_string = ''
    output = None
    if request.method == 'POST':
        app_name_string = request.POST.get('app_name', '')
        # ===== 취약 지점 =====
        # 선택된 파라미터를 제한하지 않고 셸로 실행한다(shell=True).
        # (PDF 원문은 os.system 사용 → oscmd/pdf_reference.py 에 보존.
        #  여기서는 실행 결과를 화면에 바로 보여주기 위해 결과를 캡처한다.)
        completed = subprocess.run(app_name_string, shell=True,
                                   capture_output=True, text=True)
        output = (completed.stdout or '') + (completed.stderr or '')
        if not output.strip():
            output = '(표준 출력이 없습니다 — GUI 프로그램이거나 출력이 없는 명령입니다.)'

    return render(request, 'oscmd/program.html', {
        'safe': False,
        'title': 'os.system 프로그램 실행 (취약한 코드)',
        'action_url': 'oscmd:program_vulnerable',
        'examples': PROGRAM_EXAMPLES,
        'app_name': app_name_string,
        'output': output,
        'error': None,
        'allow_program': None,
    })


# ---------------------------------------------------------------------------
# 2') os.system 프로그램 실행  -  안전한 코드 (화이트리스트)
# ---------------------------------------------------------------------------
ALLOW_PROGRAM = ['notepad', 'calc']   # PDF 원문 화이트리스트

def run_program_safe(request):
    app_name_string = ''
    output = None
    error = None
    if request.method == 'POST':
        app_name_string = request.POST.get('app_name', '')
        # ===== 안전 대책 (PDF 원문) =====
        # 선택된 파라미터를 사용가능한 시스템 명령어 일부로 제한하여 사용
        if app_name_string not in ALLOW_PROGRAM:
            error = '허용되지 않은 프로그램입니다. (화이트리스트에 없는 명령이 차단되었습니다)'
        else:
            completed = subprocess.run(app_name_string, shell=True,
                                       capture_output=True, text=True)
            output = (completed.stdout or '') + (completed.stderr or '')
            if not output.strip():
                output = '(프로그램을 실행했습니다: %s)' % app_name_string

    return render(request, 'oscmd/program.html', {
        'safe': True,
        'title': 'os.system 프로그램 실행 (안전한 코드)',
        'action_url': 'oscmd:program_safe',
        'examples': PROGRAM_EXAMPLES,
        'app_name': app_name_string,
        'output': output,
        'error': error,
        'allow_program': ALLOW_PROGRAM,
    })

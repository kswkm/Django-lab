"""
PDF 슬라이드 코드 원문 보존 (운영체제 명령어 삽입)
================================================

아래 함수들은 'PDF 시큐어 코딩(운영체제 명령어 삽입)' 슬라이드에 실린 코드를
교과서 형태 그대로 옮긴 참고용 모듈이다. (URL 과 연결되지 않는 reference)

실제 실행 가능한 형태는 oscmd/views.py 에 구현되어 있으며, 아래 코드는
슬라이드의 render(request, '/success.html') 표기 등을 포함해 원문을 보존한다.
(실제 Django 에서 템플릿 경로는 앞의 '/' 없이 'success.html' 로 써야 한다.)
"""
import os
import subprocess

from django.shortcuts import render


# ===========================================================================
# [슬라이드] 안전하지 않은 코드의 예  - os.system
# ===========================================================================
def execute_command_os_system_vuln(request):
    app_name_string = request.POST.get('app_name', '')
    # 입력받은 파라미터를 제한하지 않아 외부 입력값으로 전달된
    # 모든 프로그램이 실행될 수 있음
    os.system(app_name_string)
    return render(request, '/success.html')


# ===========================================================================
# [슬라이드] 안전한 코드의 예  - os.system + 화이트리스트
# ===========================================================================
ALLOW_PROGRAM = ['notepad', 'calc']


def execute_command_os_system_safe(request):
    app_name_string = request.POST.get('app_name', '')
    # 입력받은 파라미터를 사용가능한 시스템 명령어 일부로 제한하여 사용
    if app_name_string not in ALLOW_PROGRAM:
        return render(request, '/error.html', {'ERROR': '허용되지 않은 프로그램입니다.'})

    os.system(app_name_string)
    return render(request, '/success.html')


# ===========================================================================
# [슬라이드] 안전하지 않은 코드의 예  - subprocess shell=True
# ===========================================================================
def execute_command_subprocess_vuln(request):
    date = request.POST.get('date', '')
    # 입력받은 파라미터를 제한하지 않아 전달된 모든 프로그램이
    # 실행될 수 있음
    cmd_str = "cmd /c backuplog.bat " + date
    subprocess.run(cmd_str, shell=True)
    return render(request, '/success.html')


# ===========================================================================
# [슬라이드] 안전한 코드의 예  - subprocess 특수문자 필터 + 리스트 인자
# ===========================================================================
def execute_command_subprocess_safe(request):
    date = request.POST.get('date', '')

    # 명령어를 추가로 실행 또는 다른 명령이 실행될 수 있는 키워드에
    # 대한 예외처리
    for word in ['|', ';', '&', ':', '>', '<', '"', '\\', '!']:
        date = date.replace(word, '')

    # shell=True 옵션은 제거 하고 명령과 인자를 배열로 입력
    subprocess.run(["cmd", "/c", "backuplog.bat", date])
    return render(request, '/success.html')

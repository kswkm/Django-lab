"""
위험한 형식 파일 업로드 (Dangerous File Upload) 실습 - 실행 가능한 뷰

PDF '시큐어 코딩(위험한 형식 파일 업로드)' 슬라이드의 취약/안전 코드를 반영한다.

  - 취약한 코드 : 검증 없이 FileSystemStorage 로 그대로 저장 → 웹쉘 등 업로드 가능
  - 안전한 코드 : 개수/크기/확장자/MIME 검사 + 시그니처 + Pillow verify + 재인코딩

※ PDF 슬라이드의 코드 원문은 fileupload/pdf_reference.py 에 보존했다.
※ 4단계 검증 로직은 fileupload/validators.py 로 분리하여 단위 테스트가 가능하다.
"""
import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render

from . import validators

# 저장 경로
VULN_UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, 'vuln_uploads')
SAFE_UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, 'screenshot')


def index(request):
    """위험한 형식 파일 업로드 실습 메인 페이지."""
    return render(request, 'fileupload/index.html', {
        'count_limit': validators.FILE_COUNT_LIMIT,
        'size_limit_mb': validators.FILE_SIZE_LIMIT // (1024 * 1024),
        'white_list': ', '.join(validators.WHITE_LIST_EXT),
    })


# ---------------------------------------------------------------------------
# 취약한 코드 : 검증 없이 저장 (PDF '안전하지 않은 코드의 예')
# ---------------------------------------------------------------------------
def file_upload_vulnerable(request):
    result = None
    saved = []
    if request.method == 'POST' and request.FILES.getlist('upload_file'):
        # ===== 취약 지점 =====
        # 사용자로부터 업로드되는 파일에 대해 개수/크기/확장자/타입 검증 없이
        # 그대로 저장한다. .php, .jsp 같은 스크립트(웹쉘)도 그대로 올라간다.
        fs = FileSystemStorage(location=VULN_UPLOAD_DIR,
                               base_url=settings.MEDIA_URL + 'vuln_uploads/')
        for upload_file in request.FILES.getlist('upload_file'):
            filename = fs.save(upload_file.name, upload_file)
            saved.append({
                'name': filename,
                'url': fs.url(filename),
            })
        result = 'success'
    elif request.method == 'POST':
        result = 'error'

    return render(request, 'fileupload/upload.html', {
        'safe': False,
        'title': '파일 업로드 (취약한 코드)',
        'action_url': 'fileupload:upload_vulnerable',
        'result': result,
        'saved': saved,
        'errors': [],
    })


# ---------------------------------------------------------------------------
# 안전한 코드 : 4단계 검증 (PDF '안전한 코드의 예' + 4단계 검증 프로세스)
# ---------------------------------------------------------------------------
def file_upload_safe(request):
    result = None
    saved = []
    errors = []

    if request.method == 'POST':
        files = request.FILES.getlist('upload_file')

        # ===== 1단계: 파일 개수 제한 (PDF 안전한 코드) =====
        if len(files) == 0 or len(files) > validators.FILE_COUNT_LIMIT:
            errors.append('파일 개수 초과 (0개 또는 %d개 초과)'
                          % validators.FILE_COUNT_LIMIT)
        else:
            for upload_file in files:
                # ===== 1~3단계: MIME / 크기 / 확장자 / 시그니처 / verify =====
                is_valid, reason = validators.validate_upload(
                    filename=upload_file.name,
                    content_type=upload_file.content_type,
                    size=upload_file.size,
                    fileobj=upload_file,
                )
                if not is_valid:
                    errors.append('%s : %s' % (upload_file.name, reason))
                    continue

                # ===== 4단계: 픽셀 재인코딩(Re-draw) + UUID 파일명 + 격리 저장 =====
                try:
                    safe_name = validators.reencode_jpeg(upload_file, SAFE_UPLOAD_DIR)
                    saved.append({
                        'origin': upload_file.name,
                        'name': safe_name,
                        'url': settings.MEDIA_URL + 'screenshot/' + safe_name,
                    })
                except Exception as exc:  # noqa: BLE001 - 실습용 포괄 처리
                    errors.append('%s : 재인코딩 실패 (%s)' % (upload_file.name, exc))

        result = 'success' if saved and not errors else ('partial' if saved else 'error')

    return render(request, 'fileupload/upload.html', {
        'safe': True,
        'title': '파일 업로드 (안전한 코드)',
        'action_url': 'fileupload:upload_safe',
        'result': result,
        'saved': saved,
        'errors': errors,
    })

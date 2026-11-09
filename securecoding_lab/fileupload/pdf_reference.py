"""
PDF 슬라이드 코드 원문 보존 (위험한 형식 파일 업로드)
==================================================

'PDF 시큐어 코딩(위험한 형식 파일 업로드)' 슬라이드에 실린 코드를 교과서 형태
그대로 옮긴 참고용 모듈이다. (URL 과 연결되지 않는 reference)

실제 실행 가능한 형태는 fileupload/views.py + fileupload/validators.py 에 구현.
슬라이드의 render(request, '/success.html') 표기 등 원문을 보존한다.
"""
import os

from django.shortcuts import render
from django.core.files.storage import FileSystemStorage


# ===========================================================================
# [슬라이드] 안전하지 않은 코드의 예 - 검증 없이 저장
# ===========================================================================
def file_upload_vuln(request):
    if request.FILES['upload_file']:
        # 사용자로부터 업로드 되는 파일에 대해 검증 없이 저장하고 있어 안전하지 않다.
        upload_file = request.FILES['upload_file']  # 업로드할 파일을 불러옴
        fs = FileSystemStorage(location='media/screenshot', base_url='media/screenshot')
        # 업로드 하는 파일에 대한 크기, 개수, 확장자 등을 검증 하지 않음.
        filename = fs.save(upload_file.name, upload_file)
        return render(request, '/success.html', {'filename': filename})
    return render(request, '/error.html', {'error': '파일 업로드 실패'})


# ===========================================================================
# [슬라이드] 안전한 코드의 예 - 개수/크기/확장자/MIME 검증
# ===========================================================================
# 업로드 하는 파일에 대한 개수, 크기, 확장자 제한
FILE_COUNT_LIMIT = 5
# 업로드 하는 파일의 최대 사이즈 제한 예 ) 5MB - 5*1024*1024
FILE_SIZE_LIMIT = 5242880
# 허용하는 확장자는 화이트리스트로 관리한다.
WHITE_LIST_EXT = [
    '.jpg',
    '.jpeg'
]


def file_upload_safe(request):
    # 파일 개수 제한
    if len(request.FILES) == 0 or len(request.FILES) > FILE_COUNT_LIMIT:
        return render(request, '/error.html', {'error': '파일 개수 초과'})

    for filename, upload_file in request.FILES.items():
        # 파일 타입 체크
        if upload_file.content_type != 'image/jpeg':
            return render(request, '/error.html', {'error': '파일 타입 오류'})
        # 파일 크기 제한
        if upload_file.size > FILE_SIZE_LIMIT:
            return render(request, '/error.html', {'error': '파일사이즈 오류'})
        # 파일 확장자 검사
        file_name, file_ext = os.path.splitext(upload_file.name)
        if file_ext.lower() not in WHITE_LIST_EXT:
            return render(request, '/error.html', {'error': '파일 타입 오류'})

    fs = FileSystemStorage(location='media/screenshot', base_url='media/screenshot')
    for upload_file in request.FILES.values():
        fs.save(upload_file.name, upload_file)

    return render(request, '/success.html', {'filename': filename})

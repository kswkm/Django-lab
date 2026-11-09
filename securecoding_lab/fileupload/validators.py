"""
위험한 형식 파일 업로드 - 안전한 업로드 4단계 검증 로직

PDF '안전한 파일 업로드를 위한 4단계 검증 프로세스' 를 구현한다.
Django 에 의존하지 않는 순수 함수로 작성하여 단위 테스트가 가능하도록 분리했다.

  1단계: 서버 기본 경계 검사 - 개수/용량 제한, 확장자 화이트리스트, MIME 타입 스크리닝
  2단계: Magic Bytes(파일 시그니처) 1차 검사 - 위장된 텍스트/스크립트 파일 거부
  3단계: Pillow Image.open() & verify() 2차 구조 검사 - 손상/위조 이미지 거부
  4단계: Pillow Image.load() & 재인코딩(Re-draw) - 은닉된 악성 데이터 완전 제거
"""
import os
import uuid

from PIL import Image, UnidentifiedImageError

# --- 1단계: 서버 기본 경계 검사 기준값 (PDF 안전한 코드) ---
FILE_COUNT_LIMIT = 5                 # 1회 요청 업로드 가능 파일 수
FILE_SIZE_LIMIT = 5 * 1024 * 1024    # 최대 5MB (= 5242880)
WHITE_LIST_EXT = ['.jpg', '.jpeg']   # 허용 확장자 화이트리스트
ALLOW_MIME = 'image/jpeg'            # 허용 MIME 타입

# --- 2단계: Magic Bytes (파일 시그니처) ---
# JPEG 파일은 항상 FF D8 FF 로 시작한다.
JPEG_SIGNATURE = b'\xff\xd8\xff'


def validate_upload(filename, content_type, size, fileobj):
    """1~3단계 검증 수행.

    반환값: (is_valid: bool, reason: str)
    fileobj 는 read()/seek() 가능한 파일 객체(Django UploadedFile 또는 일반 파일).
    검증 후 파일 포인터는 항상 처음(0)으로 되돌려 둔다.
    """
    # --- 1단계: MIME 타입 스크리닝 ---
    if content_type != ALLOW_MIME:
        return False, 'MIME 타입 오류 (image/jpeg 아님)'

    # --- 1단계: 파일 크기 제한 ---
    if size > FILE_SIZE_LIMIT:
        return False, '파일 사이즈 초과 (최대 5MB)'

    # --- 1단계: 확장자 화이트리스트 검사 ---
    _, file_ext = os.path.splitext(filename)
    if file_ext.lower() not in WHITE_LIST_EXT:
        return False, '허용되지 않은 확장자'

    # --- 2단계: Magic Bytes 시그니처 검사 ---
    # 확장자/MIME 가 위장된 텍스트·스크립트 파일(renamed_text.jpg 등)을 여기서 거부.
    fileobj.seek(0)
    head = fileobj.read(len(JPEG_SIGNATURE))
    fileobj.seek(0)
    if head != JPEG_SIGNATURE:
        return False, '파일 시그니처 불일치 (위장 파일)'

    # --- 3단계: Pillow verify() 구조 검사 ---
    # 시그니처만 흉내 내고 실제 이미지 데이터가 없는 손상 파일을 거부.
    try:
        fileobj.seek(0)
        with Image.open(fileobj) as im:
            im.verify()
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError):
        fileobj.seek(0)
        return False, '이미지 구조 검증 실패 (verify)'
    finally:
        fileobj.seek(0)

    return True, 'OK'


def reencode_jpeg(fileobj, dest_dir):
    """4단계: 픽셀 데이터를 실제로 디코딩하여 재인코딩(Re-draw) 후 저장.

    - 원본 파일명을 버리고 UUID 로 난수화된 파일명을 새로 부여한다.
    - RGB 로 변환해 JPEG 로 다시 저장함으로써 메타데이터/구조에 은닉된
      악성 데이터를 완전히 제거한다.
    반환값: 저장된 안전한 파일명(str)
    """
    os.makedirs(dest_dir, exist_ok=True)
    fileobj.seek(0)
    with Image.open(fileobj) as im:
        im = im.convert('RGB')                      # 픽셀 재해석
        safe_name = uuid.uuid4().hex + '.jpg'        # 파일명 난수화 (UUID)
        im.save(os.path.join(dest_dir, safe_name), format='JPEG')  # 재인코딩 저장
    fileobj.seek(0)
    return safe_name

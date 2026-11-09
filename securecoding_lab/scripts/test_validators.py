"""
파일 업로드 4단계 검증 로직 단위 테스트 (Django 불필요, Pillow 만 필요)

    python scripts/test_validators.py

fileupload/validators.py 의 validate_upload / reencode_jpeg 가
정상/공격 파일을 기대대로 통과/거부하는지 검증한다.
"""
import io
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PIL import Image
from fileupload import validators


def _jpeg_bytes(size=(64, 64), color=(10, 20, 30)):
    buf = io.BytesIO()
    Image.new('RGB', size, color).save(buf, format='JPEG')
    buf.seek(0)
    return buf


def run():
    passed, failed = 0, 0

    def check(name, got, expect):
        nonlocal passed, failed
        ok = (got == expect)
        passed += ok
        failed += (not ok)
        print('  [%s] %-42s got=%s expect=%s' %
              ('OK' if ok else 'XX', name, got, expect))

    print('validate_upload 테스트')

    # 1) 정상 JPEG → 통과
    f = _jpeg_bytes()
    valid, _ = validators.validate_upload('good.jpg', 'image/jpeg', len(f.getvalue()), f)
    check('정상 JPEG', valid, True)

    # 2) MIME 불일치 → 거부
    f = _jpeg_bytes()
    valid, _ = validators.validate_upload('good.jpg', 'text/plain', len(f.getvalue()), f)
    check('MIME 불일치', valid, False)

    # 3) 확장자 위반(.png) → 거부
    f = _jpeg_bytes()
    valid, _ = validators.validate_upload('good.png', 'image/jpeg', len(f.getvalue()), f)
    check('확장자 위반(.png)', valid, False)

    # 4) 크기 초과 → 거부
    f = _jpeg_bytes()
    valid, _ = validators.validate_upload(
        'big.jpg', 'image/jpeg', validators.FILE_SIZE_LIMIT + 1, f)
    check('크기 초과', valid, False)

    # 5) 텍스트를 .jpg 로 위장(시그니처 불일치) → 거부
    f = io.BytesIO(b'this is plain text, not an image')
    valid, _ = validators.validate_upload('renamed_text.jpg', 'image/jpeg', 32, f)
    check('텍스트 위장(.jpg)', valid, False)

    # 6) PHP 웹쉘을 .jpg 로 위장 → 거부
    f = io.BytesIO(b"<?php echo 'x'; ?>")
    valid, _ = validators.validate_upload('evil.php.jpg', 'image/jpeg', 18, f)
    check('PHP 위장(.jpg)', valid, False)

    # 7) 시그니처만 있고 실제 이미지 아님 → verify 거부
    f = io.BytesIO(b'\xff\xd8\xff' + b'garbage-not-a-real-jpeg')
    valid, _ = validators.validate_upload('signature_only.jpg', 'image/jpeg', 26, f)
    check('시그니처만 존재', valid, False)

    print('reencode_jpeg 테스트')
    with tempfile.TemporaryDirectory() as d:
        f = _jpeg_bytes()
        name = validators.reencode_jpeg(f, d)
        exists = os.path.exists(os.path.join(d, name))
        is_uuid_jpg = name.endswith('.jpg') and len(name) == 36  # 32 hex + '.jpg'
        check('재인코딩 파일 생성', exists, True)
        check('UUID.jpg 파일명', is_uuid_jpg, True)

    print('\n결과: %d 통과 / %d 실패' % (passed, failed))
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    raise SystemExit(run())

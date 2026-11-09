"""
실습용 샘플 파일 생성기
=======================
파일 업로드 실습에 쓸 정상/공격 샘플 파일을 scripts/samples/ 에 만든다.

    python scripts/make_test_files.py

생성 파일:
  good.jpg            - 정상 JPEG (안전한 업로드에서 통과)
  evil.php            - 웹쉘 흉내 PHP 스크립트 (취약: 업로드됨 / 안전: 확장자 거부)
  evil.php.jpg        - 확장자 이중 위장 (안전: 시그니처 단계에서 거부)
  renamed_text.jpg    - 텍스트를 .jpg 로 위장 (안전: 시그니처 거부)
  signature_only.jpg  - JPEG 시그니처만 있고 실제 이미지가 아님 (안전: verify 거부)
"""
import os

from PIL import Image

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), 'samples')


def main():
    os.makedirs(SAMPLE_DIR, exist_ok=True)

    # 정상 JPEG
    img = Image.new('RGB', (64, 64), (30, 75, 143))
    img.save(os.path.join(SAMPLE_DIR, 'good.jpg'), format='JPEG')

    # 웹쉘 흉내 PHP (절대 서버에서 실행하지 말 것 - 실습 관찰용)
    with open(os.path.join(SAMPLE_DIR, 'evil.php'), 'w', encoding='utf-8') as f:
        f.write("<?php echo 'webshell sample - do not execute'; ?>\n")

    # 확장자 이중 위장: PHP 내용 + .php.jpg
    with open(os.path.join(SAMPLE_DIR, 'evil.php.jpg'), 'w', encoding='utf-8') as f:
        f.write("<?php echo 'disguised webshell'; ?>\n")

    # 텍스트를 .jpg 로 위장
    with open(os.path.join(SAMPLE_DIR, 'renamed_text.jpg'), 'w', encoding='utf-8') as f:
        f.write("this is plain text, not an image\n")

    # JPEG 시그니처만 있고 실제 이미지 데이터는 없음
    with open(os.path.join(SAMPLE_DIR, 'signature_only.jpg'), 'wb') as f:
        f.write(b'\xff\xd8\xff' + b'garbage-not-a-real-jpeg')

    print('생성 완료:', SAMPLE_DIR)
    for name in sorted(os.listdir(SAMPLE_DIR)):
        print('  -', name)


if __name__ == '__main__':
    main()

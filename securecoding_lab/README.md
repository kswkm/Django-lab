# 시큐어 코딩 실습 — 운영체제 명령어 삽입 / 위험한 형식 파일 업로드

PDF 강의자료 **『시큐어 코딩(운영체제 명령어 삽입, 위험한 형식 파일 업로드)』** 의 실습 코드를
그대로 재현한 Django 프로젝트입니다. 각 취약점을 **취약한 코드**와 **안전한 코드**로 나누어
브라우저에서 직접 공격을 재현하고 방어 효과를 확인할 수 있습니다.

> ⚠️ 교육용 로컬 실습 전용입니다. 취약 엔드포인트를 외부에 노출하지 마세요.

---

## 1. 요구 사항
- Python 3.9+
- Django 4.2+ , Pillow 10+ (`requirements.txt`)

## 2. 실행 방법 (PyCharm 터미널 또는 명령 프롬프트)

```bash
# 1) 가상환경 생성 및 활성화
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 2) 의존성 설치
pip install -r requirements.txt

# 3) 개발 서버 실행 (모델이 없어 migrate 불필요)
python manage.py runserver
```

브라우저에서 <http://127.0.0.1:8000/> 접속.

### PyCharm 에서 실행
1. `File > Open` 으로 `securecoding_lab` 폴더 열기
2. `Settings > Project > Python Interpreter` 에서 가상환경(venv) 지정 후 Django/Pillow 설치
3. 상단 실행 구성에 **Django Server** 추가하거나, `manage.py runserver` 실행

---

## 3. 실습 구성

### ① 운영체제 명령어 삽입 (`/oscmd/`)
| 구분 | 취약한 코드 | 안전한 코드 |
|------|-------------|-------------|
| Ping a device | 입력을 셸 문자열에 결합(`shell=True`) | 특수문자 제거 + IPv4 검증 + 명령/인자 리스트 분리 |
| os.system 실행 | `os.system(입력)` 그대로 | 화이트리스트 `ALLOW_PROGRAM=['notepad','calc']` |

**공격 재현 (취약 Ping 페이지 입력값)**
- Linux/macOS: `8.8.8.8 ; id` , `8.8.8.8 | cat /etc/passwd`
- Windows: `8.8.8.8 & whoami`

→ 안전한 Ping 페이지에 같은 값을 넣으면 특수문자가 제거되고 형식 검증에 걸려 **삽입 실패**.

### ② 위험한 형식 파일 업로드 (`/fileupload/`)
| 구분 | 취약한 코드 | 안전한 코드 (4단계) |
|------|-------------|---------------------|
| 저장 | 검증 없이 `FileSystemStorage.save()` | 개수/크기/확장자/MIME → 시그니처 → Pillow verify → 재인코딩 |

**4단계 검증 프로세스**
1. 서버 기본 경계 검사 — 개수(5) · 용량(5MB) · 확장자 화이트리스트(.jpg/.jpeg) · MIME(image/jpeg)
2. Magic Bytes 시그니처 검사 — JPEG `FF D8 FF` 대조 (위장 텍스트/스크립트 거부)
3. Pillow `Image.open().verify()` — 손상/위조 이미지 거부
4. Pillow 재인코딩(Re-draw) + UUID 파일명 + 웹루트 외부(`media/screenshot`) 격리 저장

**샘플 파일 생성**
```bash
python scripts/make_test_files.py   # scripts/samples/ 에 정상·공격 파일 생성
```
- `good.jpg` → 안전한 업로드에서 **통과**
- `evil.php`, `evil.php.jpg`, `renamed_text.jpg`, `signature_only.jpg` → 안전한 업로드에서 **각 단계에서 거부**
- 취약한 업로드에서는 위 파일이 **모두 그대로 저장**됨(개발 서버는 실행하지 않음)

---

## 4. 검증 (Django 없이 핵심 로직만)
```bash
python scripts/test_validators.py   # 파일 업로드 4단계 검증 로직 단위 테스트
```

---

## 5. 디렉토리 구조 · PDF 코드 매핑
```
securecoding_lab/
├── manage.py
├── config/                  # Django 설정 (settings/urls/wsgi)
├── oscmd/                   # 운영체제 명령어 삽입
│   ├── views.py             # 실행 가능한 취약/안전 뷰
│   └── pdf_reference.py     # ★ PDF 슬라이드 코드 원문 보존 (os.system / subprocess)
├── fileupload/              # 위험한 형식 파일 업로드
│   ├── views.py             # 실행 가능한 취약/안전 뷰
│   ├── validators.py        # 4단계 검증 로직 (단위 테스트 대상)
│   └── pdf_reference.py     # ★ PDF 슬라이드 코드 원문 보존 (업로드 취약/안전)
├── templates/               # 공통·성공·오류 화면
├── media/screenshot/        # 안전한 업로드 저장 위치
└── scripts/                 # 샘플 생성기, 단위 테스트, backuplog 배치
```

PDF 슬라이드의 코드 **원문**은 각 앱의 `pdf_reference.py` 에 교과서 형태 그대로 보존했고,
실제 **실행 가능한 형태**는 `views.py` 에 구현했습니다. (슬라이드의 `render(request, '/success.html')`
표기는 원문에 보존, 실행 코드에서는 올바른 템플릿 경로로 구현)

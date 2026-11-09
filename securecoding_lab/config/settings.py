"""
Django settings for 시큐어 코딩 실습 프로젝트 (운영체제 명령어 삽입 / 위험한 형식 파일 업로드)

학습용 로컬 실습 설정이다. DEBUG=True, 단순 SECRET_KEY 등은 실습 편의를 위한 것이며
실제 서비스에 그대로 사용하면 안 된다.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# 실습용 키. 운영 환경에서는 반드시 교체한다.
SECRET_KEY = 'django-insecure-secure-coding-lab-demo-key-do-not-use-in-prod'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'oscmd',
    'fileupload',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# 모델을 사용하지 않지만 Django 가 요구하므로 기본 sqlite 를 지정한다.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

# 업로드 파일 저장 위치 (웹 루트와 분리된 media 디렉토리)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 실습 편의: 업로드 용량 한도를 넉넉히 (안전 로직에서 별도 검증한다)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

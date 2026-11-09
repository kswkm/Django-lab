from django.apps import AppConfig


class FileuploadConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fileupload'
    verbose_name = '위험한 형식 파일 업로드'

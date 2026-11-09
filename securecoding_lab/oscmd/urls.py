from django.urls import path
from . import views

app_name = 'oscmd'

urlpatterns = [
    path('', views.index, name='index'),
    # 운영체제 명령어 삽입 - Ping a device 공격 데모 (PDF 공격 절차)
    path('ping/vulnerable/', views.ping_vulnerable, name='ping_vulnerable'),
    path('ping/safe/', views.ping_safe, name='ping_safe'),
    # os.system 화이트리스트 예제 (PDF 안전하지 않은/안전한 코드)
    path('program/vulnerable/', views.run_program_vulnerable, name='program_vulnerable'),
    path('program/safe/', views.run_program_safe, name='program_safe'),
]

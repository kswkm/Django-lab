from django.urls import path
from . import views

app_name = 'fileupload'

urlpatterns = [
    path('', views.index, name='index'),
    path('vulnerable/', views.file_upload_vulnerable, name='upload_vulnerable'),
    path('safe/', views.file_upload_safe, name='upload_safe'),
]

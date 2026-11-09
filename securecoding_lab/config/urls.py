from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('oscmd/', include('oscmd.urls')),
    path('fileupload/', include('fileupload.urls')),
]

# 실습 중 업로드된 이미지를 브라우저에서 확인할 수 있도록 media 서빙 (DEBUG 전용)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

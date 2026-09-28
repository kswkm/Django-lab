from django.urls import path

from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('data/', views.data_view, name='data'),
]

from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.home_view, name='home'),  # Главная страница приложения
    path('template/<int:template_id>/', views.view_report, name='view_report'),
]
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('view/<int:template_id>/', views.view_report, name='view_report'),
    path('print/<int:template_id>/', views.print_report, name='print_report'),
    path('pdf/<int:template_id>/', views.generate_pdf_report, name='generate_pdf'),
]
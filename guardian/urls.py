from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('glioma_analysis/', views.glioma_analysis, name='glioma_analysis'),
    path('blood_cell_analysis/', views.blood_cell_analysis, name='blood_cell_analysis'),
    path('patients/', views.patients, name='patients'),
    path('sobre/', views.about, name='about'),
    path('registrar/', views.register_patients, name='register_patients'),
    path('contact/', views.contact, name='contact'),
    path('glioma_analysis/<int:paciente_id>/', views.analise_paciente, name='analise_paciente'),  # Usando a view de glioma_analysis
    path('editar_paciente/<int:paciente_id>/', views.editar_paciente, name='editar_paciente'),
    path('apagar_paciente/<int:paciente_id>/', views.apagar_paciente, name='apagar_paciente'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
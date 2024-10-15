import cv2
import numpy as np
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Paciente
from .forms import PacienteForm

# Página de login
def login(request):
    return render(request, 'guardian/pages/login/login.html')

# Página inicial
def home(request):
    return render(request, 'guardian/pages/home.html')

# Página de análise de glioma
def glioma_analysis(request):
    search_query = request.GET.get('search', '')  # Captura a string de pesquisa
    selected_patient_id = request.GET.get('patient_id', '')  # Captura o ID do paciente selecionado
    processed_image_url = None  # Inicializa a variável para a imagem processada

    # Filtra os pacientes com base no campo de pesquisa, ou busca todos
    if search_query:
        pacientes = Paciente.objects.filter(nome_completo__icontains=search_query)
    else:
        pacientes = Paciente.objects.all()

    # Se houver um paciente selecionado, pega o paciente pelo ID
    paciente = None
    if selected_patient_id:
        paciente = get_object_or_404(Paciente, id=selected_patient_id)

        if request.method == 'POST':
            # Processa a imagem
            img_path = paciente.exame.path
            img = cv2.imread(img_path)

            # Processamento da imagem
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
            limiar = 135
            _, thresh = cv2.threshold(gray, limiar, 255, cv2.THRESH_BINARY)

            # Salvar a imagem processada
            processed_image_name = 'processed_' + str(paciente.id) + '.png'
            processed_image_path = os.path.join(settings.MEDIA_ROOT, processed_image_name)
            cv2.imwrite(processed_image_path, thresh)

            # Atualiza a URL da imagem processada
            processed_image_url = os.path.join(settings.MEDIA_URL, processed_image_name)

    return render(request, 'guardian/pages/glioma/glioma_analysis.html', {
        'pacientes': pacientes,
        'paciente': paciente,
        'search_query': search_query,
        'selected_patient_id': selected_patient_id,
        'processed_image_url': processed_image_url,  # Passa a URL da imagem processada
    })

# Página de lista de pacientes com funcionalidade de pesquisa
def patients(request):
    query = request.GET.get('q')
    if query:
        pacientes = Paciente.objects.filter(nome_completo__icontains=query)
    else:
        pacientes = Paciente.objects.all()
    return render(request, 'guardian/pages/patients/patients.html', {'pacientes': pacientes})

# Página de cadastro de pacientes
def register_patients(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('patients')  # Redirecionar para a lista de pacientes após o cadastro
    else:
        form = PacienteForm()
    return render(request, 'guardian/pages/register_patients/register_patients.html', {'form': form})

# Página "Sobre"
def about(request):
    return render(request, 'guardian/pages/about/about.html')

# Página de contato
def contact(request):
    return render(request, 'guardian/pages/contact/contact.html')

# Página de análise de células sanguíneas
def blood_cell_analysis(request):
    return render(request, 'guardian/home.html')

# Página de análise de paciente (para análise de imagem)
def analise_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    return render(request, 'guardian/pages/glioma/glioma_analysis.html', {'paciente': paciente})

def editar_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    if request.method == 'POST':
        paciente.nome_completo = request.POST['nome']
        paciente.idade = request.POST['idade']
        paciente.sexo = request.POST['sexo']
        paciente.save()
        return redirect('patients')  # Redireciona para a lista de pacientes

def apagar_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    if request.method == 'POST':
        paciente.delete()
        return redirect('patients')  # Redireciona para a lista de pacientes

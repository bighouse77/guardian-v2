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

    # Filtra os pacientes com base no campo de pesquisa, ou busca todos
    if search_query:
        pacientes = Paciente.objects.filter(nome_completo__icontains=search_query)
    else:
        pacientes = Paciente.objects.all()

    # Se houver um paciente selecionado, pega o paciente pelo ID
    paciente = None
    if selected_patient_id:
        paciente = get_object_or_404(Paciente, id=selected_patient_id)

    return render(request, 'guardian/pages/glioma/glioma_analysis.html', {
        'pacientes': pacientes,
        'paciente': paciente,  # Paciente selecionado
        'search_query': search_query,
        'selected_patient_id': selected_patient_id,
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

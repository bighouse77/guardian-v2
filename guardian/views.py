import cv2
import numpy as np
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Paciente
from .forms import PacienteForm
from .algorithm import process_image, analyze_single_image
from django.urls import reverse
from django.utils.http import urlencode
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.platypus import Frame
from reportlab.platypus import Frame, KeepInFrame

# Página de login
def login(request):
    return render(request, 'guardian/pages/login/login.html')

# Página inicial
def home(request):
    return render(request, 'guardian/pages/home.html')

# Página de análise de glioma
def glioma_analysis(request):
    search_query = request.GET.get('search', '')  
    selected_patient_id = request.GET.get('patient_id', '')  
    processed_image_url = None  
    tumor_result = None

    if search_query:
        pacientes = Paciente.objects.filter(nome_completo__icontains=search_query)
    else:
        pacientes = Paciente.objects.all()

    paciente = None
    if selected_patient_id:
        paciente = get_object_or_404(Paciente, id=selected_patient_id)

        if request.method == 'POST':
            img_path = paciente.exame.path
            processed_image_name = process_image(img_path, paciente.id)
            processed_image_url = os.path.join(settings.MEDIA_URL, processed_image_name)
            model_path = os.path.join(settings.BASE_DIR, 'guardian/model/model.h5')
            tumor_result = analyze_single_image(img_path, model_path)

            # Redireciona para a página de laudo usando query string para a imagem
            query_params = urlencode({
                'tumor_result': tumor_result,
                'processed_image_url': processed_image_url
            })
            return redirect(f"{reverse('laudo', args=[paciente.id])}?{query_params}")

    return render(request, 'guardian/pages/glioma/glioma_analysis.html', {
        'pacientes': pacientes,
        'paciente': paciente,
        'search_query': search_query,
        'selected_patient_id': selected_patient_id,
        'processed_image_url': processed_image_url,
        'tumor_result': tumor_result,
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
        return redirect('patients')  # Redireciona para a lista de pacientes
    
# Página de laudo
def laudo(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    tumor_result = request.GET.get('tumor_result')
    processed_image_url = request.GET.get('processed_image_url')

    return render(request, 'guardian/pages/laudo/laudo.html', {
        'paciente': paciente,
        'tumor_result': tumor_result,
        'processed_image_url': processed_image_url,
        'gerar_laudo_pdf_url': reverse('gerar_laudo_pdf', args=[paciente.id]),
    })

# Gerar PDF do laudo
def gerar_laudo_pdf(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    tumor_result = request.GET.get('tumor_result')
    processed_image_url = request.GET.get('processed_image_url')

    print("Processed Image URL:", processed_image_url)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="laudo.pdf"'

    # Criar um documento PDF
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    title_style = ParagraphStyle(name='Title', fontSize=16, alignment=1, spaceAfter=12, leading=25)

    # Criar borda
    border = 20  # Margem da borda
    frame = Frame(border, border, width=doc.width - 2*border, height=doc.height - 2*border, showBoundary=1)

    # Cabeçalho com a imagem do QR Code
    qr_code_path = 'guardian\static\guardian\images\QRCode.png'
    logo = Image(qr_code_path, width=120, height=120)  # Ajuste de tamanho para manter a proporção

    # Adicionar a imagem ao PDF
    elements.append(logo)

    # Informações de contato
    contato_info = [
        "Av. Dr. Maximiliano Baruto, 500 - Jardim Universitário",
        "(19) 98957-5065",
        "Código validador: XXXX",
        "Controle: 202212/111"
    ]
    for info in contato_info:
        elements.append(Paragraph(info, normal_style))

    elements.append(Spacer(1, 12))  # Espaçamento

    # Título
    title = Paragraph("LAUDO DE RESSONÂNCIA MAGNÉTICA ANÁLISE DE TUMOR CEREBRAL", title_style)
    elements.append(title)

    # Informações do paciente
    elements.append(Spacer(1, 12))  # Espaçamento
    elements.append(Paragraph(f"<strong>Nome:</strong> {paciente.nome_completo}", normal_style))
    elements.append(Paragraph(f"<strong>Sexo:</strong> {paciente.sexo}", normal_style))
    elements.append(Paragraph("<strong>Convênio:</strong> SUS", normal_style))

    # Resultado do exame
    resultado_texto = "<strong>Resultado do exame:</strong> "
    if tumor_result == '1':
        resultado = Paragraph("<strong>POSITIVO</strong>", ParagraphStyle(name='Red', textColor=colors.red))
    else:
        resultado = Paragraph("<strong>NEGATIVO</strong>", ParagraphStyle(name='Green', textColor=colors.green))

    elements.append(Paragraph(resultado_texto, normal_style))
    elements.append(resultado)

    # Conclusão
    if tumor_result == '1':
        conclusao = ("O exame de imagem realizado revelou a presença de uma massa expansiva compatível com tumor cerebral na "
                     "região frontal esquerda. As características morfológicas são sugestivas de glioma, sendo recomendado o "
                     "encaminhamento para avaliação neurocirúrgica e biópsia para confirmação do diagnóstico. O paciente deverá "
                     "iniciar acompanhamento especializado o mais breve possível.")
    else:
        conclusao = ("O exame de imagem realizado não revelou a presença de qualquer massa expansiva ou lesão compatível com tumor "
                     "cerebral. As estruturas encefálicas encontram-se dentro dos limites da normalidade. Não foram observadas "
                     "alterações significativas. Recomendado acompanhamento clínico de rotina conforme necessidade.")

    elements.append(Paragraph(f"<strong>Conclusão:</strong> {conclusao}", normal_style))

    elements.append(Spacer(1, 12)) 

    # Imagem Radiológica
    if processed_image_url:
        image_path = os.path.join(settings.MEDIA_ROOT, processed_image_url.replace(settings.MEDIA_URL, ''))  # Caminho absoluto
        if os.path.exists(image_path):  # Verifique se a imagem existe
            image = Image(image_path, width=400, height=300)  # Ajuste as dimensões conforme necessário
            elements.append(image)
        else:
            elements.append(Paragraph("Imagem não disponível. Arquivo não encontrado.", normal_style))
    else:
        elements.append(Paragraph("Imagem não disponível.", normal_style))
        
    elements.append(Spacer(1, 24))  # Espaçamento

    # Rodapé
    elements.append(Paragraph("Fundação Hermínio Ometto", normal_style))
    elements.append(Paragraph("Dr. Abel Casagrande", normal_style))
    elements.append(Paragraph("CRM: XXX", normal_style))

    # Montar documento e salvar
    doc.build(elements)

    return response

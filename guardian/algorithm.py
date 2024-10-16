import cv2
import os
from django.conf import settings

def process_image(image_path, patient_id):
    # Carregar a imagem
    img = cv2.imread(image_path)

    # Processamento da imagem
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    limiar = 135
    _, thresh = cv2.threshold(gray, limiar, 255, cv2.THRESH_BINARY)

    # Nome do arquivo processado
    processed_image_name = f'processed_{patient_id}.png'
    processed_image_path = os.path.join(settings.MEDIA_ROOT, processed_image_name)

    # Salvar a imagem processada
    cv2.imwrite(processed_image_path, thresh)

    # Retornar o caminho da imagem processada
    return processed_image_name

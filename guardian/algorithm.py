import os
import numpy as np
import cv2
from django.conf import settings
from PIL import Image
import torchvision.transforms as transforms
import matplotlib.pyplot as plt

def process_image(image_path, patient_id):
    # Definir transformações básicas sem rotação, apenas redimensionando
    transform = transforms.Compose(
        [
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
        ]
    )

    # Carregar a imagem
    img = Image.open(image_path).convert('L')  # Converte diretamente para escala de cinza

    # Aplicar transformações
    img_transformed = transform(img)

    # Converter de tensor para numpy array para manipulação
    img_np = img_transformed.numpy().squeeze()  # Remove dimensões extras

    # Melhorar contraste usando normalização manual
    img_np = (img_np - img_np.min()) / (img_np.max() - img_np.min())  # Normaliza para 0-1
    img_np = np.clip(img_np * 255, 0, 255).astype(np.uint8)  # Converte para 0-255

    # Aplicar um limiar para destacar as áreas brilhantes (tumores)
    _, img_thresh = cv2.threshold(img_np, 150, 255, cv2.THRESH_BINARY)

    # Aplicar negativo (inversão de cores)
    img_negative = 255 - img_thresh

    # Visualizar a imagem transformada
    plt.imshow(img_negative, cmap='gray')
    plt.title("Imagem Processada (Negativo)")
    plt.axis('off')

    # Salvar a imagem processada
    processed_image_name = f'processed_negative_{patient_id}.png'
    processed_image_path = os.path.join(settings.MEDIA_ROOT, processed_image_name)
    Image.fromarray(img_negative).save(processed_image_path)

    return processed_image_name
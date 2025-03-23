# =========================================================
#   Notebook de Processamento Digital de Imagens
#   Usando OpenCV (cv2)
# =========================================================

import cv2
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# Função auxiliar para exibir imagens lado a lado no notebook
# ---------------------------------------------------------
mousePos = []
def click_event(event, x, y, flags, params, xSq=2,ySq = 2): 
  
    # checking for left mouse clicks 
    if event == cv2.EVENT_LBUTTONDOWN: 
  
        # displaying the coordinates 
        # on the Shell 
        print(x, ' ', y) 
  
        # displaying the coordinates 
        # on the image window 
        for k in range (-xSq,xSq,1):
            for l in range (-ySq,ySq,1):
                imagem_colorida[y+k,x+l] = [43,255,0]
        mousePos.append([y,x])
         

def show_images(images, titles=None, cmap=None, size=(15, 5)):
    """
    Exibe uma lista de imagens lado a lado usando Matplotlib.
    images: lista de arrays (BGR ou escala de cinza)
    titles: lista de títulos para cada imagem
    cmap: se deseja exibir em escala de cinza, use 'gray'
    size: tamanho da figura
    """
    n = len(images)
    if titles is None:
        titles = [f"Imagem {i}" for i in range(n)]
    plt.figure(figsize=size)
    for i, img in enumerate(images):
        plt.subplot(1, n, i+1)
        if cmap == 'gray':
            cv2.imshow(img, cmap='gray')
        else:
            # Se for imagem em BGR, converte para RGB antes de exibir
            if len(img.shape) == 3:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                plt.imshow(img_rgb)
            else:
                plt.imshow(img, cmap='gray')
        plt.title(titles[i])
        plt.axis('off')
    #plt.show()

# ---------------------------------------------------------rc
# 1) Leitura da imagem
# ---------------------------------------------------------
# Substitua "caminho_da_imagem.jpg" pelo arquivo que deseja analisar.
imagem_colorida = cv2.imread("/home/ufabc/Downloads/images.jpeg")

# Se a imagem não for carregada, a variável ficará como None.
# Verificamos para evitar erros.
if imagem_colorida is None:
    raise ValueError("Não foi possível carregar a imagem. Verifique o caminho informado.")

# Exibir a imagem original
#show_images([imagem_colorida], ["Original"])
numClick = [0]
inputPXL = []
cv2.imshow('Image',imagem_colorida)
cv2.setMouseCallback('Image', click_event, numClick)


while len(mousePos) <= 3:  
  cv2.waitKey(10)
  cv2.imshow('Image',imagem_colorida)
  
oldTransform = np.float32(mousePos)

#Distancia para frame
#Ideia - Pegar distancia em X e distancia em Y - Maior é a horizontal
dist = []
for i in range(1,len(mousePos)):
    dy0 = mousePos[0][0]
    dx0 = mousePos[0][1]
    dy = mousePos[i][0]
    dx = mousePos[i][1]
    
    h = abs(dy-dy0)
    l = abs(dx-dx0)
    length = ((h**2)+(l**2))**(1/2)
    dist.append(length)
print(dist)
h,w = np.float32(np.partition(dist, 1)[0:2])
h = int(h)
w = int(w)
    
newTransform = np.float32([[0,0],[0,w],[h,0],[h,w]])
M = cv2.getPerspectiveTransform(oldTransform,newTransform)
dst = cv2.warpPerspective(imagem_colorida,M,(w,h))

cv2.imshow('Output', dst)

cv2.waitKey(50000)

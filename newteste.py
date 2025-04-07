import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
from morph import *
import copy
print(os.getcwd())
#from morph import *

mousePos = []

# ---------------------------------------------------------
# Função auxiliar para exibir imagens lado a lado no notebook
# ---------------------------------------------------------
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
            plt.imshow(img, cmap='gray')
        else:
            # Se for imagem em BGR, converte para RGB antes de exibir
            if len(img.shape) == 3:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                plt.imshow(img_rgb)
            else:
                plt.imshow(img, cmap='gray')
        plt.title(titles[i])
        plt.axis('off')
    plt.show()

#Função para detectar o click do mouse
def click_event(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Coordenada capturada: ({x}, {y})")
        mousePos.append([x, y])

        # Exibir ponto clicado na imagem
        cv2.circle(imagem_colorida, (x, y), 5, (43, 255, 0), -1)
        cv2.imshow('Image', imagem_colorida)

        # Quando quatro pontos forem coletados, iniciar transformação
        if len(mousePos) == 4:
            processar_transformacao()

#Função para processar a paralaxe do sistema
def processar_transformacao():
    global mousePos
    global dst
    # Garantir que temos 4 pontos exatos
    if len(mousePos) != 4:
        print("Erro: é necessário selecionar exatamente 4 pontos.")
        return
    
    # Ordenar pontos corretamente para evitar distorções
    #mousePos = sorted(mousePos, key=lambda p: (p[1], p[0]))  # Primeiro ordena por Y, depois por X
    print (mousePos)
    # Criar matriz de transformação
    oldTransform = np.float32(mousePos)

    # Determinar largura e altura do novo recorte
    x_vals = [p[0] for p in mousePos]
    y_vals = [p[1] for p in mousePos]

    w = max(x_vals) - min(x_vals)
    h = max(y_vals) - min(y_vals)

    newTransform = np.float32([[0, 0], [w, 0], [0, h], [w, h]])

    # Aplicar transformação
    M = cv2.getPerspectiveTransform(oldTransform, newTransform)
    dst = cv2.warpPerspective(imagem_colorida, M, (w, h))

    # Exibir resultado
    cv2.imshow('Output', dst)
    return dst

# Carregar imagem
imagem_colorida = cv2.imread("./IMG_20250323_0002.jpg")

if imagem_colorida is None:
    raise ValueError("Não foi possível carregar a imagem. Verifique o caminho.")

cv2.imshow('Image', imagem_colorida)
cv2.setMouseCallback('Image', click_event)

cv2.waitKey(0)
cv2.destroyAllWindows()

#Start post processing
grayImage = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
#cv2.imshow('gray',grayImage)
#cv2.waitKey(0)
#cv2.destroyAllWindows()

#Imagem salva
#-------------------------------------------------------------------------------------------------------------------------------
#Função para separar o pixel do histograma
def __derivada(pixelAnt,pixelDep,array):
        """
        Calcula a derivada entre dois pontos em uma lista.

        Args:
            pixelAnt (int): Índice do ponto anterior.
            pixelDep (int): Índice do ponto seguinte.
            array (list): Lista de valores.

        Returns:
            float: A derivada entre os pontos.
        """
        #Derivada de um pixel: dy/dx = (y2-y1)/1
        return (array[pixelDep]-array[pixelAnt])
def encontrar_pixel_mais_prox(ponto, comprimentoDeOnda):
        """
        Encontra o índice do ponto mais próximo em uma lista de comprimentos de onda.

        Args:
            ponto (float): O ponto de referência.
            comprimentoDeOnda (list): Lista de comprimentos de onda.

        Returns:
            int: O índice do ponto mais próximo.
        """
        #Encontra a distancia minima entre os pontos do espectro
        proximidadePonto = [x-ponto for x in comprimentoDeOnda] 
        index = ((np.abs(proximidadePonto)).argmin())
        return index
def isolar_pico(centroPico,intensidadeEspectro, comprimentoDeOnda=None):
        """
        Isola um pico em um espectro.

        Args:
            centroPico (float): O centro estimado do pico.
            intensidadeEspectro (list): Lista de intensidades do espectro.
            comprimentoDeOnda (list, optional): Lista de comprimentos de onda. Se não fornecido, usa o valor padrão.

        Returns:
            tuple: Uma tupla contendo o comprimento de onda do pico, do ponto de background à esquerda e à direita.
        """
        #Caso nao seja passado um comprimento de onda
        if (comprimentoDeOnda == None):
            #Utilizar o comprimento de onda encontrado no arquivo
            comprimentoDeOnda = []
            for i in range(len(intensidadeEspectro)):
                comprimentoDeOnda.append(i)
        #Variaveis para retornar
        pontoPico = -1
        pontoBackgroundEsq = -1
        pontoBackgroundDir = -1
        #Variaveis para verificar pontos fora do intervalo de comprimentos de onda
        enableDerivadaEsq = False
        enableDerivadaDir = False
        #Criando variaveis para procurar o pico e os backgrounds - Usada inicialmente para procurar o pico 
        possivelPonto = encontrar_pixel_mais_prox(centroPico, comprimentoDeOnda)
        #Caso o ponto nao esteja bem comportado dentro do espectro
        if possivelPonto == 0 or possivelPonto == len(comprimentoDeOnda) - 1:
            #Caso o ponto eseja proximo da lateral esquerda
            if possivelPonto == 0:
                enableDerivadaDir = True
                pontoBackgroundEsq = 0
                derivadaEsq = -1
            #Caso o ponto esteja proximo da lateral direita
            else:
                enableDerivadaEsq = True
                pontoBackgroundDir = len(comprimentoDeOnda)-1
                derivadaDir= -1
            #derivada = -1 -garantir que ela seja detectada como menor que 0
            #para a rotina detectar mais tarde
        else:
            #Permitir o calculo para as duas derivadas
            enableDerivadaEsq = True
            enableDerivadaDir = True
        
        #Funcao para procurar pico
        #Variaveis auxiliares
        if enableDerivadaEsq:
            derivadaEsq = __derivada(possivelPonto,possivelPonto -1,intensidadeEspectro)
        if enableDerivadaDir:
            derivadaDir = __derivada(possivelPonto,possivelPonto + 1,intensidadeEspectro)
        #Manter a funcao rodando enquanto o ponto nao for um pico encontrado pelas derivadas
        while(derivadaEsq >= 0 or derivadaDir >= 0):
            #Verifica a se o pico esta subindo para...
            #A esquerda:
            if derivadaEsq > 0 and derivadaDir < 0 :
                possivelPonto -= 1
            #A direita:
            elif derivadaEsq < 0 and derivadaDir > 0 :
                possivelPonto += 1
            #Caso as duas derivadas sejam positivas
            elif derivadaEsq > 0 and derivadaDir > 0:
                #Verificar qual esta com maior tendencia de subida
                if derivadaEsq > derivadaDir:
                    possivelPonto -= 1
                else:
                    possivelPonto += 1
            #Caso o pico esteja saturado - valores maximos iguais
            elif derivadaEsq == 0 or derivadaDir == 0:
                #A derivada esta proxima do centro
                break
            #Recalcular as derivadas no novo possivel ponto
            if (possivelPonto > 0 and possivelPonto < len(comprimentoDeOnda)):
                derivadaEsq = __derivada(possivelPonto,possivelPonto -1,intensidadeEspectro)
                derivadaDir = __derivada(possivelPonto,possivelPonto + 1,intensidadeEspectro)
        
        #Salva o pico encontrado
        pontoPico = possivelPonto
        
        #Funcoes para procurar os valores de background
        #Background esquerdo:
        #Reseta as variaveis
        possivelPonto = pontoPico
        derivadaEsq = __derivada(possivelPonto,possivelPonto -1,intensidadeEspectro)
        #Procura pelo menor ponto para background
        while (derivadaEsq <= 0):
            possivelPonto -= 1
            derivadaEsq = __derivada(possivelPonto,possivelPonto -1,intensidadeEspectro)
        #Salva o ponto de background
        pontoBackgroundEsq = possivelPonto
        
        #Background direito:
        #Reseta as variaveis
        possivelPonto = pontoPico
        derivadaDir = __derivada(possivelPonto,possivelPonto + 1,intensidadeEspectro) 
        #Procura pelo menor ponto para background
        while (derivadaDir <= 0):
            possivelPonto += 1
            derivadaDir = __derivada(possivelPonto,possivelPonto + 1,intensidadeEspectro) 
        #Salva o ponto de background
        pontoBackgroundDir = possivelPonto

        #Retorna os valores da funcao
        return comprimentoDeOnda[pontoPico],comprimentoDeOnda[pontoBackgroundEsq],comprimentoDeOnda[pontoBackgroundDir]

'''Inserir uma interface (terminal?) para ciclar entre as funcionalidades'''
#Histograma
mousePos = []
def get_pixel_value(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Coordenada capturada: ({x}, {y})")
        mousePos.append([x, y])
        #print(mousePos)
        # Sai do click 
        cv2.destroyAllWindows()
        #cv2.waitKey(0)

#Equalized image
equalizedImage = cv2.equalizeHist(grayImage)
totalImage = np.vstack((grayImage,equalizedImage))
#Plot do histograma
cv2.imshow('Image', totalImage)
cv2.setMouseCallback('Image', get_pixel_value)
cv2.waitKey(0)
#cv2.destroyAllWindows()

#Get mouse position
x,y = mousePos[0]

#Switch case based on the pixel height 
#Get old height
h = len(grayImage)
selectedImage = []
#Check if clicked image was the equalized one
if y >= h:
    selectedImage = equalizedImage
    #Remove the height of previous image
    y = y-h
#Else
else:
    selectedImage = grayImage
#Get pixel color value
pixelValue = selectedImage[y][x]

#Plot histogram
imgHist = mm.hist(selectedImage)
plt.plot(range(len(imgHist)),imgHist,color='tab:orange')
plt.axvline(pixelValue)
plt.show()
def th_calculator(image,leftTH,rigthTH):
    #Create mask between left and rigth TH
    #Get value to reshape
    h,w = image.shape
    #Create new string
    thImage = copy.deepcopy(image.ravel())
    #Get threshold
    for i in range(len(image.ravel())):
        if image.ravel()[i] >= leftTH and image.ravel()[i] <= rigthTH:
            #Add value to treshold
            thImage[i] = 255
        else:
            thImage[i] = 0

    #Reshape image
    thImage = thImage.reshape(h,w)
    cv2.imshow('Threshold',thImage)
    cv2.waitKey(0)
    return thImage
latch = True
while latch:
    Value = input("Digite '0' para utilizar a derivada e '1' para utilizar threshold numérico ('s' para salvar e sair, 'x' para sair sem salvar): ")
    if Value == '0':
        #Get histogram treshold
        centerValue,leftTH,rigthTH = isolar_pico(pixelValue,imgHist)
        newImage = th_calculator(selectedImage,leftTH,rigthTH)
    elif Value == '1':
        imgHist = mm.hist(selectedImage)
        plt.plot(range(len(imgHist)),imgHist,color='tab:orange')
        plt.axvline(pixelValue)
        plt.show()
        print(f'Valor do pixel selecionado: {pixelValue}')
        leftTH = int(input('Janela esquerda: '))
        rigthTH = int(input('Janela direita: '))
        newImage = th_calculator(selectedImage,leftTH,rigthTH)
    elif Value == 's':
        selectedImage = newImage
        latch = False
    elif Value == 'x':
        latch = False


# ---------------------------------------------------------
# 2) Filtragem de Imagens (Remoção de ruídos, melhoria de nitidez)
# ---------------------------------------------------------
# Exemplo de filtragem com blur Gaussiano para redução de ruído
gauss = cv2.GaussianBlur(selectedImage, (5, 5), 0)

# Exemplo de filtro de mediana (geralmente eficaz para remover ruídos do tipo sal e pimenta)
mediana = cv2.medianBlur(selectedImage, 5)

show_images([selectedImage, gauss, mediana],
            ["Original", "Gaussian Blur", "Mediana"])

# ---------------------------------------------------------
# 4) Histograma e Equalização
# ---------------------------------------------------------
# Converter para escala de cinza
imagem_cinza = cv2.cvtColor(selectedImage, cv2.COLOR_BGR2GRAY)

# Equalização de histograma
imagem_equalizada = cv2.equalizeHist(imagem_cinza)

show_images([imagem_cinza, imagem_equalizada],
            ["Escala de Cinza Original", "Equalizada"],
            cmap='gray')

# Exemplo de exibição de histogramas
# (apenas para fins de visualização, não é obrigatório)
plt.figure(figsize=(10, 4))
plt.hist(imagem_cinza.ravel(), 256, [0, 256])
plt.title("Histograma - Imagem Original (em Cinza)")
plt.show()

plt.figure(figsize=(10, 4))
plt.hist(imagem_equalizada.ravel(), 256, [0, 256])
plt.title("Histograma - Imagem Equalizada (em Cinza)")
plt.show()

# ---------------------------------------------------------
# 5) Morfologia Matemática (Segmentação/Realce de bordas, remoção de ruídos)
# ---------------------------------------------------------
# Exemplo de abertura (opening) para remover ruídos pontuais
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
imagem_opening = cv2.morphologyEx(imagem_equalizada, cv2.MORPH_OPEN, kernel)

# Exemplo de dilatação para destacar estruturas claras
imagem_dilatada = cv2.dilate(imagem_opening, kernel, iterations=1)

show_images([imagem_equalizada, imagem_opening, imagem_dilatada],
            ["Equalizada", "Abertura (Opening)", "Dilatação"],
            cmap='gray')

# ---------------------------------------------------------
# 6) Segmentação Avançada
#    Aplicaremos Watershed + Transformada de Distância + Labeling
# ---------------------------------------------------------

# (a) Threshold inicial para separar fundo/objeto de forma grosseira
_, thresh = cv2.threshold(imagem_equalizada, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

# (b) Operações morfológicas para remover falhas no threshold
# Por exemplo: abertura seguida de dilatação
kernel_seg = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel_seg, iterations=2)
sure_bg = cv2.dilate(opening, kernel_seg, iterations=3)  # área de fundo provável

# (c) Transformada de distância para encontrar regiões que são certamente primeiro plano
dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
# Ajuste do fator 0.7 conforme a imagem
_, sure_fg = cv2.threshold(dist_transform, 0.7*dist_transform.max(), 255, 0)
sure_fg = np.uint8(sure_fg)

# (d) Região desconhecida (fica entre o primeiro plano e o fundo prováveis)
unknown = cv2.subtract(sure_bg, sure_fg)

# (e) Labeling para separar componentes
# connectedComponents retorna o número de rótulos e a matriz de labels
num_objetos, markers = cv2.connectedComponents(sure_fg)

# Importante: para usar watershed, precisamos que os marcadores sejam > 0
# e que pixels de fundo sejam marcados como 0.
# Uma técnica comum: soma 1 para que o fundo (antes 0) vire 1, e os objetos comecem em 2.
markers = markers + 1

# Marca a região desconhecida como 0
markers[unknown == 255] = 0

# Converter original para BGR se necessário (já está em BGR, mas vamos garantir outra cópia)
imagem_ws = imagem_colorida.copy()

# (f) Aplicar watershed
markers = cv2.watershed(imagem_ws, markers)

# Onde o watershed marcou como -1, temos fronteiras
imagem_ws[markers == -1] = [0, 0, 255]  # pinta as fronteiras de vermelho

# ---------------------------------------------------------
# Exibir resultados da segmentação
# ---------------------------------------------------------
show_images([
    thresh,
    opening,
    sure_bg,
    dist_transform,
    sure_fg
],
[
    "Threshold Otsu",
    "Opening",
    "Fundo provável",
    "Transformada de Distância",
    "Primeiro plano provável"
],
cmap='gray',
size=(20, 5))

show_images([
    unknown,
    imagem_ws
],
[
    "Região desconhecida",
    "Watershed (Bordas em Vermelho)"
],
size=(10, 5))

# Realizando o 'Labeling' final (para contagem de objetos)
# Basta lembrar que connectedComponents já retornou 'num_objetos'
# Observe que esse 'num_objetos' inclui também o rótulo de fundo
print(f"Número de rótulos (incluindo fundo): {num_objetos}")
print("Obs.: O rótulo 0 representa o fundo na imagem binária.")

# Fim do notebook
print("Processamento concluído!")

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import copy
from morph import mm

# --------------------------------------------------------
# Função de utilidade para exibir imagens lado a lado
# --------------------------------------------------------
def show_images(images, titles=None, cmap=None, size=(15, 5)):
    n = len(images)
    if titles is None:
        titles = [f"Imagem {i}" for i in range(n)]
    plt.figure(figsize=size)
    for i, img in enumerate(images):
        plt.subplot(1, n, i+1)
        if cmap == 'gray':
            plt.imshow(img, cmap='gray')
        else:
            if len(img.shape) == 3:
                plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            else:
                plt.imshow(img, cmap='gray')
        plt.title(titles[i])
        plt.axis('off')
    plt.show()

# --------------------------------------------------------
# Seleção de ROI via clique do mouse e transformação perspectiva
# --------------------------------------------------------
roi_points = []  # variável global para armazenar os pontos

def select_roi(image):
    """
    Permite selecionar uma região de interesse (ROI) clicando 4 pontos.
    Após a seleção dos 4 pontos, a função calcula a transformação perspectiva 
    e retorna a ROI.
    """
    roi_points = []
    temp_image = image.copy()
    window_name = "Selecione ROI"

    def click_event(event, x, y, flags, param):
        nonlocal temp_image, roi_points  # Permite acessar as variáveis da função externa
        if event == cv2.EVENT_LBUTTONDOWN:
            roi_points.append([x, y])
            # Desenhar um círculo na posição clicada
            cv2.circle(temp_image, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow(window_name, temp_image)
    
    cv2.imshow(window_name, temp_image)
    cv2.setMouseCallback(window_name, click_event)
    
    # Aguarda até que 4 pontos sejam selecionados
    while len(roi_points) < 4:
        # Usamos waitKey(1) para atualizar a janela e processar os eventos de mouse
        if cv2.waitKey(1) & 0xFF == 27:  # Se pressionar Esc, interrompe a seleção
            break
            
    cv2.destroyWindow(window_name)

    if len(roi_points) != 4:
        raise ValueError("Foram selecionados menos de 4 pontos.")

    pts = np.float32(roi_points)
    w = int(max(pts[:, 0]) - min(pts[:, 0]))
    h = int(max(pts[:, 1]) - min(pts[:, 1]))
    dst_pts = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
    M = cv2.getPerspectiveTransform(pts, dst_pts)
    roi = cv2.warpPerspective(image, M, (w, h))
    return roi

# --------------------------------------------------------
# Conversão para escala de cinza e equalização do histograma
# --------------------------------------------------------
def convert_to_gray(image):
    """Converte a imagem para escala de cinza."""
    if len(image.shape) == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image

def equalize_image(image):
    """Equaliza o histograma da imagem em escala de cinza."""
    return cv2.equalizeHist(image)

# --------------------------------------------------------
# Exibição do histograma e seleção de um pixel
# --------------------------------------------------------
def plot_histogram(image, pixel_value=None, title="Histograma"):
    hist = mm.hist(image)
    plt.figure(figsize=(8, 4))
    plt.plot(range(len(hist)), hist, color='tab:orange')
    if pixel_value is not None:
        plt.axvline(pixel_value, color='red')
    plt.title(title)
    plt.show()
    return hist

def get_pixel_value(image):
    """
    Permite que o usuário clique em um pixel da imagem para selecioná-lo.
    Retorna o valor do pixel (para uma imagem em cinza).
    """
    coords = []
    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            coords.append((x, y))
            cv2.destroyWindow("Selecione Pixel")
    cv2.imshow("Selecione Pixel", image)
    cv2.setMouseCallback("Selecione Pixel", click_event)
    cv2.waitKey(0)
    if not coords:
        raise ValueError("Nenhum pixel selecionado.")
    x, y = coords[0]
    return image[y, x]

# --------------------------------------------------------
# Limiarização (thresholding)
# --------------------------------------------------------
def threshold_by_derivative(image, pixel_value, hist):
    """
    Determina os limites do threshold (left e right) baseando-se na derivada do histograma.
    Aqui é usada a função isolar_pico para isolar o pico do espectro.
    """
    center, left_thresh, right_thresh = isolar_pico(pixel_value, hist)
    return left_thresh, right_thresh

def isolar_pico(centroPico, intensidadeEspectro, comprimentoDeOnda=None):
    """
    Isole um pico em um espectro.
    Se 'comprimentoDeOnda' não for fornecido, usa os índices como referência.
    Retorna (pico, background esquerdo, background direito).
    (Esta é uma versão simplificada; adapte conforme sua necessidade.)
    """
    if comprimentoDeOnda is None:
        comprimentoDeOnda = list(range(len(intensidadeEspectro)))
        
    def derivada(pixelAnt, pixelDep, array):
        return array[pixelDep] - array[pixelAnt]
    
    def encontrar_pixel_mais_prox(ponto, compOnda):
        diffs = [abs(x - ponto) for x in compOnda]
        return diffs.index(min(diffs))
    
    possivelPonto = encontrar_pixel_mais_prox(centroPico, comprimentoDeOnda)
    # Para simplificar, definimos uma janela fixa em torno do pico:
    pontoPico = possivelPonto
    pontoBackgroundEsq = max(0, pontoPico - 10)
    pontoBackgroundDir = min(len(comprimentoDeOnda)-1, pontoPico + 10)
    return comprimentoDeOnda[pontoPico], comprimentoDeOnda[pontoBackgroundEsq], comprimentoDeOnda[pontoBackgroundDir]

def apply_numeric_threshold(image, leftTH, rightTH):
    """Aplica limiarização na imagem usando os limites numéricos."""
    th_image = np.where((image >= leftTH) & (image <= rightTH), 255, 0).astype(np.uint8)
    return th_image

# --------------------------------------------------------
# Filtragem da imagem
# --------------------------------------------------------
def apply_filters(image):
    """Aplica filtragens de redução de ruído: Gaussian e mediana."""
    gaussian = cv2.GaussianBlur(image, (5, 5), 0)
    median = cv2.medianBlur(image, 5)
    return gaussian, median

# --------------------------------------------------------
# Operações morfológicas
# --------------------------------------------------------
def morphological_operations(image):
    """
    Realiza operações morfológicas na imagem equalizada.
    Executa abertura (opening) e dilatação.
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    opening = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    dilation = cv2.dilate(opening, kernel, iterations=1)
    return opening, dilation

# --------------------------------------------------------
# Segmentação via Watershed
# --------------------------------------------------------
def watershed_segmentation(color_image, equalized_image):
    """
    Aplica segmentação usando watershed. 
    Retorna os marcadores e a imagem com as bordas (marcadas em vermelho).
    """
    # Limiarização inicial (Otsu)
    _, thresh = cv2.threshold(equalized_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Operações morfológicas para limpar a imagem
    kernel_seg = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel_seg, iterations=2)
    sure_bg = cv2.dilate(opening, kernel_seg, iterations=3)
    
    # Transformada de distância para identificar primeiro plano
    dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    _, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
    sure_fg = np.uint8(sure_fg)
    
    # Região desconhecida (entre fundo e primeiro plano)
    unknown = cv2.subtract(sure_bg, sure_fg)
    
    # Labeling: marcadores para componentes conectados
    num_objetos, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1  # fundo passa a ser 1 e objetos a partir de 2
    markers[unknown == 255] = 0

    # Aplicar watershed
    markers = cv2.watershed(color_image.copy(), markers)
    color_image[markers == -1] = [0, 0, 255]  # bordas em vermelho
    return markers, color_image

# --------------------------------------------------------
# Função principal que integra todas as etapas
# --------------------------------------------------------
def main():
    # Carregar imagem
    image_path = "./IMG_20250323_0002.jpg"
    image_colorida = cv2.imread(image_path)
    if image_colorida is None:
        raise ValueError("Não foi possível carregar a imagem. Verifique o caminho.")
    
    # 1) Seleção da ROI com transformação perspectiva
    roi = select_roi(image_colorida)
    cv2.imshow("ROI", roi)
    cv2.waitKey(0)
    cv2.destroyWindow("ROI")
    
    # 2) Processamento de pré-visualização: conversão para cinza e equalização
    gray = convert_to_gray(roi)
    equalized = equalize_image(gray)
    
    # 3) Visualização do histograma e seleção do pixel para referência do limiar
    hist = plot_histogram(equalized, title="Histograma da imagem equalizada")
    pixel_val = get_pixel_value(equalized)
    print("Valor do pixel selecionado:", pixel_val)
    
    # 4) Limiarização: escolha entre utilizar derivada ou threshold numérico
    modo = input("Digite '0' para usar derivada e '1' para threshold numérico: ")
    if modo == '0':
        leftTH, rightTH = threshold_by_derivative(equalized, pixel_val, hist)
    elif modo == '1':
        leftTH = int(input("Janela esquerda: "))
        rightTH = int(input("Janela direita: "))
    else:
        raise ValueError("Modo inválido.")
    
    th_image = apply_numeric_threshold(equalized, leftTH, rightTH)
    cv2.imshow("Imagem Limiarizada", th_image)
    cv2.waitKey(0)
    cv2.destroyWindow("Imagem Limiarizada")
    
    # 5) Aplicação de filtros para redução de ruídos
    gauss, median = apply_filters(th_image)
    show_images([th_image, gauss, median],
                ["Limiarizada", "Gaussian Blur", "Filtro Mediana"],
                cmap='gray')
    
    # 6) Operações morfológicas (abertura e dilatação)
    opening, dilation = morphological_operations(equalized)
    show_images([equalized, opening, dilation],
                ["Imagem Equalizada", "Abertura (Opening)", "Dilatação"],
                cmap='gray')
    
    # 7) Segmentação Avançada via Watershed
    markers, ws_image = watershed_segmentation(roi, equalized)
    show_images([ws_image], ["Watershed (Bordas em Vermelho)"])
    
    print("Processamento concluído.")
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
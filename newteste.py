import cv2
import numpy as np

# ============================
# Função para ordenar os 4 pontos
# ============================
def ordenar_pontos(pontos):
    """
    Ordena os 4 pontos no formato:
    [top-left, top-right, bottom-left, bottom-right]
    """
    pontos = np.array(pontos, dtype="float32")

    soma = pontos.sum(axis=1)
    dif = np.diff(pontos, axis=1)

    ordenado = np.zeros((4, 2), dtype="float32")
    ordenado[0] = pontos[np.argmin(soma)]     # top-left
    ordenado[3] = pontos[np.argmax(soma)]     # bottom-right
    ordenado[1] = pontos[np.argmin(dif)]      # top-right
    ordenado[2] = pontos[np.argmax(dif)]      # bottom-left

    return ordenado

# ============================
# Função principal de recorte
# ============================
def processar_transformacao():
    global mousePos

    if len(mousePos) != 4:
        print("Erro: é necessário selecionar exatamente 4 pontos.")
        return

    oldTransform = ordenar_pontos(mousePos)

    # Define nova largura e altura baseadas na geometria dos pontos
    (tl, tr, bl, br) = oldTransform
    wA = np.linalg.norm(br - bl)
    wB = np.linalg.norm(tr - tl)
    hA = np.linalg.norm(tr - br)
    hB = np.linalg.norm(tl - bl)

    width = int(max(wA, wB))
    height = int(max(hA, hB))

    newTransform = np.float32([
        [0, 0],
        [width, 0],
        [0, height],
        [width, height]
    ])

    M = cv2.getPerspectiveTransform(oldTransform, newTransform)
    dst = cv2.warpPerspective(imagem_original, M, (width, height))

    cv2.imshow('Recorte', dst)

# ============================
# Função de clique do mouse
# ============================
def click_event(event, x, y, flags, params):
    global mousePos, imagem_para_cliques

    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Coordenada capturada: ({x}, {y})")
        mousePos.append([x, y])

        # Desenhar ponto clicado
        cv2.circle(imagem_para_cliques, (x, y), 5, (43, 255, 0), -1)
        cv2.imshow('Image', imagem_para_cliques)

        if len(mousePos) == 4:
            processar_transformacao()

            # Resetar pontos e imagem de exibição
            mousePos = []
            imagem_para_cliques = imagem_original.copy()
            cv2.imshow('Image', imagem_para_cliques)

# ============================
# Execução principal
# ============================

# Carrega imagem
imagem_original = cv2.imread("images.jpg")

if imagem_original is None:
    raise ValueError("Não foi possível carregar a imagem.")

imagem_para_cliques = imagem_original.copy()
mousePos = []

# Mostra imagem
cv2.imshow('Image', imagem_para_cliques)
cv2.setMouseCallback('Image', click_event)

# Espera até apertar ESC
while True:
    key = cv2.waitKey(1)
    if key == 27:  # Tecla ESC
        break

cv2.destroyAllWindows()
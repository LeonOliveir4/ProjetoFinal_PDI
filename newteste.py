import cv2
import numpy as np

mousePos = []

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

def processar_transformacao():
    global mousePos
    # Garantir que temos 4 pontos exatos
    if len(mousePos) != 4:
        print("Erro: é necessário selecionar exatamente 4 pontos.")
        return
    
    # Ordenar pontos corretamente para evitar distorções
    mousePos = sorted(mousePos, key=lambda p: (p[1], p[0]))  # Primeiro ordena por Y, depois por X

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

# Carregar imagem
imagem_colorida = cv2.imread("/home/ufabc/Downloads/images.jpeg")

if imagem_colorida is None:
    raise ValueError("Não foi possível carregar a imagem. Verifique o caminho.")

cv2.imshow('Image', imagem_colorida)
cv2.setMouseCallback('Image', click_event)

cv2.waitKey(0)
cv2.destroyAllWindows()
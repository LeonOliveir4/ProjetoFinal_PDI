import cv2
import numpy as np
import matplotlib.pyplot as plt
import copy
import tkinter as tk
from tkinter import filedialog, messagebox

# Importa as funções definidas (ou copie-as aqui)
from morph import mm  # caso precise de alguma função da biblioteca morph
# As funções abaixo foram definidas no exemplo de modularização:
# - select_roi(image)
# - convert_to_gray(image)
# - equalize_image(image)
# - apply_numeric_threshold(image, leftTH, rightTH)
# - apply_filters(image) --> retorna (gauss, median)
# - morphological_operations(image) --> retorna (opening, dilation)
# - watershed_segmentation(color_image, equalized_image)
#
# Certifique-se de que estas funções estão definidas antes ou faça a importação adequada.

# Exemplo de função para selecionar ROI (já ajustada conforme correções anteriores)
def select_roi(image):
    """
    Permite selecionar uma região de interesse (ROI) clicando 4 pontos.
    Após a seleção, aplica a transformação perspectiva e retorna a ROI.
    """
    roi_points = []
    temp_image = image.copy()
    window_name = "Selecione ROI"

    def click_event(event, x, y, flags, param):
        nonlocal temp_image, roi_points
        if event == cv2.EVENT_LBUTTONDOWN:
            roi_points.append([x, y])
            cv2.circle(temp_image, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow(window_name, temp_image)

    cv2.imshow(window_name, temp_image)
    cv2.setMouseCallback(window_name, click_event)

    # Aguarda até que 4 pontos sejam selecionados ou o usuário pressione Esc
    while len(roi_points) < 4:
        if cv2.waitKey(1) & 0xFF == 27:
            break
    cv2.destroyWindow(window_name)

    if len(roi_points) != 4:
        raise ValueError("Foram selecionados menos de 4 pontos na ROI.")
    pts = np.float32(roi_points)
    w = int(max(pts[:, 0]) - min(pts[:, 0]))
    h = int(max(pts[:, 1]) - min(pts[:, 1]))
    dst_pts = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
    M = cv2.getPerspectiveTransform(pts, dst_pts)
    roi = cv2.warpPerspective(image, M, (w, h))
    return roi

# Funções de processamento de imagem (versões simplificadas ou conforme seu código)
def convert_to_gray(image):
    if len(image.shape) == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image

def equalize_image(image):
    return cv2.equalizeHist(image)

def apply_numeric_threshold(image, leftTH, rightTH):
    th_image = np.where((image >= leftTH) & (image <= rightTH), 255, 0).astype(np.uint8)
    return th_image

def apply_filters(image):
    gaussian = cv2.GaussianBlur(image, (5, 5), 0)
    median = cv2.medianBlur(image, 5)
    return gaussian, median

def morphological_operations(image):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    opening = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    dilation = cv2.dilate(opening, kernel, iterations=1)
    return opening, dilation

def watershed_segmentation(color_image, equalized_image):
    # Limiarização inicial usando Otsu
    _, thresh = cv2.threshold(equalized_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # Operação morfológica para remover ruídos
    kernel_seg = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel_seg, iterations=2)
    sure_bg = cv2.dilate(opening, kernel_seg, iterations=3)
    # Transformada de distância para identificar primeiro plano
    dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    _, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg, sure_fg)
    # Labeling
    num_labels, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1  # Background passa a ter valor 1
    markers[unknown == 255] = 0
    markers = cv2.watershed(color_image.copy(), markers)
    color_image[markers == -1] = [0, 0, 255]  # Borda em vermelho
    return markers, color_image

# Interface gráfica com Tkinter
selected_image = None  # imagem colorida original
processed_image = None

def select_image():
    global selected_image
    path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")])
    if path:
        selected_image = cv2.imread(path)
        if selected_image is None:
            messagebox.showerror("Erro", "Não foi possível carregar a imagem.")
        else:
            # Exibe uma pré-visualização rápida
            cv2.imshow("Imagem Selecionada", selected_image)
            cv2.waitKey(1000)
            cv2.destroyWindow("Imagem Selecionada")
            lbl_file.config(text=path)

def run_pipeline():
    global selected_image, processed_image
    if selected_image is None:
        messagebox.showerror("Erro", "Selecione uma imagem primeiro!")
        return

    img = selected_image.copy()

    # Se o usuário escolher selecionar a ROI
    if var_roi.get():
        try:
            img = select_roi(img)
        except Exception as e:
            messagebox.showerror("Erro na ROI", str(e))
            return

    # Se o usuário escolher equalizar a imagem (apenas funciona bem para imagens em tons de cinza)
    if var_equalize.get():
        gray = convert_to_gray(img)
        img = equalize_image(gray)

    # Se o usuário escolher aplicar threshold numérico
    if var_threshold.get():
        try:
            left_val = int(entry_left.get())
            right_val = int(entry_right.get())
        except ValueError:
            messagebox.showerror("Erro", "Digite valores numéricos para o Threshold!")
            return
        img = apply_numeric_threshold(img, left_val, right_val)

    # Se o usuário escolher aplicar filtragem (Gaussian ou Mediana)
    if var_filter.get():
        gauss, median = apply_filters(img)
        # Para exemplificar, escolhemos o filtro mediano para o processamento subsequente
        img = median

    # Se o usuário escolher operações morfológicas
    if var_morph.get():
        opening, dilation = morphological_operations(img)
        # Neste exemplo, usamos a imagem dilatada
        img = dilation

    processed_image = img

    # Se o usuário escolher segmentação watershed, precisamos de uma imagem em cor e uma igualizada
    if var_watershed.get():
        # Se a equalização não foi aplicada anteriormente, a convertemos
        if not var_equalize.get():
            gray = convert_to_gray(img)
            equalized_img = equalize_image(gray)
        else:
            equalized_img = img
        markers, ws_image = watershed_segmentation(selected_image, equalized_img)
        cv2.imshow("Segmentação Watershed", ws_image)
        cv2.waitKey(0)
        cv2.destroyWindow("Segmentação Watershed")

    cv2.imshow("Imagem Processada", processed_image)
    cv2.waitKey(0)
    cv2.destroyWindow("Imagem Processada")

# Cria a janela principal da interface
root = tk.Tk()
root.title("Interface de Processamento de Imagens")

# Botão para selecionar a imagem
btn_select = tk.Button(root, text="Selecionar Imagem", command=select_image)
btn_select.pack(pady=10)

lbl_file = tk.Label(root, text="Nenhuma imagem selecionada")
lbl_file.pack()

# Checkbuttons para escolher as transformações desejadas
var_roi = tk.BooleanVar()
chk_roi = tk.Checkbutton(root, text="Selecionar ROI", variable=var_roi)
chk_roi.pack()

var_equalize = tk.BooleanVar()
chk_equalize = tk.Checkbutton(root, text="Equalizar Imagem (grayscale)", variable=var_equalize)
chk_equalize.pack()

var_threshold = tk.BooleanVar()
chk_threshold = tk.Checkbutton(root, text="Aplicar Threshold Numérico", variable=var_threshold)
chk_threshold.pack()

# Entradas para os valores do threshold
frame_threshold = tk.Frame(root)
frame_threshold.pack(pady=5)
tk.Label(frame_threshold, text="Left:").grid(row=0, column=0)
entry_left = tk.Entry(frame_threshold, width=5)
entry_left.grid(row=0, column=1)
tk.Label(frame_threshold, text="Right:").grid(row=0, column=2)
entry_right = tk.Entry(frame_threshold, width=5)
entry_right.grid(row=0, column=3)

var_filter = tk.BooleanVar()
chk_filter = tk.Checkbutton(root, text="Aplicar Filtragem", variable=var_filter)
chk_filter.pack()

var_morph = tk.BooleanVar()
chk_morph = tk.Checkbutton(root, text="Operações Morfológicas", variable=var_morph)
chk_morph.pack()

var_watershed = tk.BooleanVar()
chk_watershed = tk.Checkbutton(root, text="Segmentação Watershed", variable=var_watershed)
chk_watershed.pack()

btn_run = tk.Button(root, text="Aplicar Transformações", command=run_pipeline)
btn_run.pack(pady=10)

root.mainloop()

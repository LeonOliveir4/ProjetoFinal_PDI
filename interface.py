import cv2
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image
from threading import *
import copy

# --------------------------------------------------------
# Utilidade para esperar e fechar janela OpenCV
# --------------------------------------------------------
def wait_to_close_cv_window(window_name, timeout_ms=1):
    while True:
        key = cv2.waitKey(timeout_ms) & 0xFF
        if key in [27, ord('q'), ord(' ')] or cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break
    cv2.destroyWindow(window_name)

# --------------------------------------------------------
# Funções de processamento
# --------------------------------------------------------
def select_roi(image):
    roi_points = []
    temp_image = image.copy()
    window_name = "Selecione Regiao de Interesse"

    def click_event(event, x, y, flags, param):
        nonlocal temp_image, roi_points
        if event == cv2.EVENT_LBUTTONDOWN:
            roi_points.append([x, y])
            cv2.circle(temp_image, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow(window_name, temp_image)

    cv2.imshow(window_name, temp_image)
    cv2.setMouseCallback(window_name, click_event)

    while len(roi_points) < 4:
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break
        if cv2.waitKey(1) & 0xFF == 27:
            break
    cv2.destroyWindow(window_name)

    if len(roi_points) != 4:
        raise ValueError("Foram selecionados menos de 4 pontos na ROI.")

    pts = np.array(roi_points, dtype="float32")

    # Ordena os pontos: topo-esquerda, topo-direita, baixo-esquerda, baixo-direita
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    ordered_pts = np.zeros((4, 2), dtype="float32")
    ordered_pts[0] = pts[np.argmin(s)]       # top-left
    ordered_pts[2] = pts[np.argmax(s)]       # bottom-right
    ordered_pts[1] = pts[np.argmin(diff)]    # top-right
    ordered_pts[3] = pts[np.argmax(diff)]    # bottom-left

    (tl, tr, br, bl) = ordered_pts

    # Calcula largura e altura do novo retângulo
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = int(max(widthA, widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = int(max(heightA, heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(ordered_pts, dst)
    roi = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return roi

def convert_to_gray(image):
    if len(image.shape) == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image

def equalize_image(image):
    eq = cv2.equalizeHist(image)
    #plot_histogram(eq, title="Histograma após equalização")
    return eq

def plot_histogram(image, title="Histograma"):
    hist = cv2.calcHist([image], [0], None, [256], [0, 256])
    plt.figure(figsize=(8, 4))
    plt.plot(hist, color='tab:blue')
    plt.title(title)
    plt.xlabel('Intensidade')
    plt.ylabel('Frequência')
    plt.grid(True)
    plt.draw()
    plt.pause(0.001)
    plt.waitforbuttonpress()
    plt.close()

def apply_numeric_threshold(image, leftTH, rightTH):
    return np.where((image >= leftTH) & (image <= rightTH), 255, 0).astype(np.uint8)

def apply_filters(image):
    gaussian = cv2.GaussianBlur(image, (5, 5), 0)
    median = cv2.medianBlur(image, 5)
    return gaussian, median

def morphological_operations(image):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    opening = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    dilation = cv2.dilate(opening, kernel, iterations=1)
    return opening, dilation

def watershed_segmentation(original_image, mask_image):
    # Garante que a imagem seja BGR para desenhar contornos coloridos
    if len(original_image.shape) == 2 or original_image.shape[2] == 1:
        original_image = cv2.cvtColor(original_image, cv2.COLOR_GRAY2BGR)

    # Usa threshold adaptativo no lugar de Otsu
    thresh = cv2.adaptiveThreshold(mask_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 10)

    # Morfologia com menos iterações (preserva texto)
    kernel_seg = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel_seg, iterations=1)
    sure_bg = cv2.dilate(opening, kernel_seg, iterations=2)

    dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    _, sure_fg = cv2.threshold(dist_transform, 0.4 * dist_transform.max(), 255, 0)

    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg, sure_fg)

    _, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0

    result = original_image.copy()
    markers = np.int32(markers)
    markers = cv2.watershed(result, markers)
    result[markers == -1] = [0, 0, 255]  # contornos em vermelho

    return result


# --------------------------------------------------------
# Interface Tkinter
# --------------------------------------------------------
selected_image = None
processed_image = None
equalized_flag = False

root = tk.Tk()
root.title("Interface de Processamento de Imagens")

def select_image():
    global selected_image, equalized_flag
    path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")])
    if path:
        selected_image = cv2.imread(path)
        if selected_image is None:
            messagebox.showerror("Erro", "Não foi possível carregar a imagem.")
        else:
            cv2.imshow("Imagem Selecionada", selected_image)
            for _ in range(300):
                key = cv2.waitKey(1) & 0xFF
                if key in [27, ord('q'), ord(' ')] or cv2.getWindowProperty("Imagem Selecionada", cv2.WND_PROP_VISIBLE) < 1:
                    break
            if cv2.getWindowProperty("Imagem Selecionada", cv2.WND_PROP_VISIBLE) >= 1:
                cv2.destroyWindow("Imagem Selecionada")
            lbl_file.config(text=path)
            chk_watershed.config(state='disabled')
            var_watershed.set(False)
            equalized_flag = False

def select_webcam():
    global selected_image, equalized_flag
    webcam = cv2.VideoCapture(0)

    if webcam.isOpened():
        print("Webcam Encontrada")
        webcamCheck, frame = webcam.read()
        print("Dados do frame:",frame.shape)
        while webcamCheck:
            webcamCheck, selected_image = webcam.read()
            if frame is None:
                messagebox.showerror("Erro", "Não foi possível carregar a imagem.")
                webcam.release()
                cv2.destroyAllWindows()
                break
            else:
                cv2.imshow("Webcam", selected_image)
                key = cv2.waitKey(30) #& 0xFF
                # if cv2.getWindowProperty("Imagem Selecionada", cv2.WND_PROP_VISIBLE) >= 1:
                #     cv2.destroyWindow("Imagem Selecionada")
                #print(cv2.getWindowProperty("Webcam", cv2.WND_PROP_VISIBLE))
                if key != -1 or cv2.getWindowProperty("Webcam", cv2.WND_PROP_VISIBLE) != 1:
                    if key != -1:
                        cv2.destroyWindow("Webcam")
                    cv2.imshow("Imagem Selecionada", selected_image)
                    for _ in range(300):
                        key = cv2.waitKey(1) & 0xFF
                        if key in [27, ord('q'), ord(' ')] or cv2.getWindowProperty("Imagem Selecionada", cv2.WND_PROP_VISIBLE) < 1:
                            break
                    if cv2.getWindowProperty("Imagem Selecionada", cv2.WND_PROP_VISIBLE) >= 1:
                        cv2.destroyWindow("Imagem Selecionada")
                    lbl_file.config(text="Webcam")
                    chk_watershed.config(state='disabled')
                    var_watershed.set(False)
                    equalized_flag = False
                    break
    webcam.release()


def on_equalize_checked():
    if var_equalize.get():
        chk_watershed.config(state='normal')
    else:
        chk_watershed.config(state='disabled')
        var_watershed.set(False)

def run_pipeline():
    global selected_image, processed_image, equalized_flag

    if selected_image is None:
        messagebox.showerror("Erro", "Selecione uma imagem primeiro!")
        return
    # Impede ROI com Threshold sem valores preenchidos
    if not var_equalize.get() and var_threshold.get():
        # left_val = entry_left.get()
        # right_val = entry_right.get()
        #if not left_val or not right_val:
        messagebox.showerror("Erro", "Você ativou Threshold sem equalizar. Selecione a equalização para utilizar o Threshold.")
        return

    img = selected_image.copy()
    if var_roi.get():
        try:
            img = select_roi(img)
        except Exception as e:
            messagebox.showerror("Erro na ROI", str(e))
            return

    if var_equalize.get():
        gray = convert_to_gray(img)
        img = equalize_image(gray)
        equalized_flag = True

    if var_threshold.get():
        try:
            imgTH = TH_window(img)
            pass
            #left_val = int(entry_left.get())
            #right_val = inentry_right.get())
        except ValueError:
            messagebox.showerror("Erro", "Digite valores numéricos para o Threshold!")
            return
        #img = apply_numeric_threshold(img, left_val, right_val)
        img = copy.deepcopy(imgTH)

    if var_filter.get():
        _, median = apply_filters(img)
        img = median

    if var_morph.get():
        _, dilation = morphological_operations(img)
        img = dilation

    processed_image = img.copy()

    if var_watershed.get():
        if not equalized_flag:
            messagebox.showwarning("Atenção", "A equalização deve ser feita antes de aplicar Watershed.")
            return
        equalized = convert_to_gray(processed_image)
        ws_img = watershed_segmentation(processed_image, equalized)
        cv2.imshow("Watershed Result", ws_img)
        wait_to_close_cv_window("Watershed Result")
    else:
        cv2.imshow("Imagem Processada", processed_image)
        wait_to_close_cv_window("Imagem Processada")

def TH_window(img):
    h,w = img.shape
    global THleft, THright, imagemORG, imgLbl, imgMod   
    imagemORG = imgMod = img
    imagemTK = ImageTk.PhotoImage(Image.fromarray(imagemORG))
    window = tk.Toplevel(root)
    window.title("Threshold")
    wid = 300
    if w > wid:
        wid = w
    window.geometry(f'{wid}x{100+h}')
    imgLbl = tk.Label(window,image=imagemTK)
    imgLbl.pack()
    frame_threshold = tk.Frame(window)
    frame_threshold.pack(pady=5)
    tk.Label(frame_threshold, text="Mínimo:").grid(row=0, column=0)
    THleft = tk.Scale(frame_threshold, from_=0, to=255, orient=tk.HORIZONTAL, command=atualizar_TH)
    THleft.grid(row=0,column=1)
    # entry_left = tk.Entry(frame_threshold, width=5)
    # entry_left.grid(row=0, column=1)
    tk.Label(frame_threshold, text="Máximo:").grid(row=0, column=2)
    THright = tk.Scale(frame_threshold, from_=0, to=255, orient=tk.HORIZONTAL, command=atualizar_TH)
    THright.grid(row=0, column=3)
    #tk.Button(window, text="Atualizar", command=found_TH).pack(pady=10)
    tk.Button(window, text="Finalizar", command=window.destroy).pack(pady=10)
    root.wait_window(window)
    return imgMod

def atualizar_TH(slider):
    global imgMod
    left_val = THleft.get()
    right_val = THright.get()
    imagem = apply_numeric_threshold(imagemORG, left_val, right_val)
    novaImagem = ImageTk.PhotoImage(Image.fromarray(imagem))
    imgLbl.configure(image=novaImagem)
    imgLbl.image = novaImagem 
    imgMod = imagem


def image_save():
    filename = filedialog.asksaveasfile(filetypes=[('All Files','.'),('PNG','.png'),('JPEG','.jpeg'),('JPG','.jpg')],mode='w', defaultextension=".png")
    if filename is None: # asksaveasfile return `None` if dialog closed with "cancel".
        return
    cv2.imwrite(filename.name,processed_image)
    print('Imagem salva com sucesso!')
    

# --------------------------------------------------------
# Construção da interface
# --------------------------------------------------------
btn_select = tk.Button(root, text="Selecionar Imagem", command=select_image)
btn_select.pack(pady=10)

btn_cam = tk.Button(root, text="Capturar Webcam", command=select_webcam)
btn_cam.pack(pady=10)

lbl_file = tk.Label(root, text="Nenhuma imagem selecionada")
lbl_file.pack()

var_roi = tk.BooleanVar()
tk.Checkbutton(root, text="Selecionar ROI", variable=var_roi).pack()

var_equalize = tk.BooleanVar()
chk_equalize = tk.Checkbutton(root, text="Equalizar Imagem (grayscale)", variable=var_equalize, command=on_equalize_checked)
chk_equalize.pack()

var_threshold = tk.BooleanVar()
tk.Checkbutton(root, text="Aplicar Threshold Numérico", variable=var_threshold).pack()

frame_threshold = tk.Frame(root)
frame_threshold.pack(pady=5)
# tk.Label(frame_threshold, text="Mínimo:").grid(row=0, column=0)
# entry_left = tk.Scale(frame_threshold, from_=0, to=255, orient=tk.HORIZONTAL)
# entry_left.grid(row=0,column=1)
# # entry_left = tk.Entry(frame_threshold, width=5)
# # entry_left.grid(row=0, column=1)
# tk.Label(frame_threshold, text="Máximo:").grid(row=0, column=2)
# entry_right = tk.Scale(frame_threshold, from_=0, to=255, orient=tk.HORIZONTAL)
# entry_right.grid(row=0, column=3)
#entry_right = tk.Entry(frame_threshold, width=5)
#entry_right.grid(row=0, column=3)

var_filter = tk.BooleanVar()
tk.Checkbutton(root, text="Aplicar Filtragem", variable=var_filter).pack()

var_morph = tk.BooleanVar()
tk.Checkbutton(root, text="Operações Morfológicas", variable=var_morph).pack()

var_watershed = tk.BooleanVar()
chk_watershed = tk.Checkbutton(root, text="Segmentação Watershed", variable=var_watershed)
chk_watershed.pack()
chk_watershed.config(state='disabled')

btn_run = tk.Button(root, text="Aplicar Transformações", command=run_pipeline)
btn_run.pack(pady=10)

btn_save = tk.Button(root, text="Salvar Imagem", command=image_save)
btn_save.pack(pady=10)

root.mainloop()

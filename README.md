# ProjetoFinal_PDI

Projeto da disciplina de Processamento Digital de Imagens (PDI) - UFABC

**Autores:**
- Leonardo Pires de Oliveira - 11201920744
- Leonardo Fabiano de Souza - 11201721317
- Murilo Valentim Alves - 11202130884
- Stephany Caroline C. Santanna - 11201920287

---

## 🧠 Objetivo do Projeto

Desenvolver uma ferramenta interativa para aplicar técnicas de Processamento Digital de Imagens (PDI) com foco na **realção de letras ou elementos visuais de difícil leitura**, presentes em:
- documentos escaneados;
- componentes eletrônicos (ex: chips);
- superfícies texturizadas ou desgastadas.

A aplicação foi criada com interface Tkinter e funcionalidades modulares que permitem selecionar regiões, visualizar histograma, aplicar filtros, binarizações, morfologia e segmentação por Watershed.

---

## 🛠️ Funcionalidades (e conceitos teóricos)

### ✅ **Seleção de ROI com correção por perspectiva**
Permite ao usuário selecionar 4 pontos em qualquer região da imagem. A função `cv2.getPerspectiveTransform()` é usada para retificar a região e corrigir inclinação/torção (ex: chips inclinados).

### ✅ **Conversão para grayscale e equalização de histograma**
Usa `cv2.cvtColor()` e `cv2.equalizeHist()` para:
- reduzir informação de cor;
- redistribuir os níveis de intensidade;
- melhorar o contraste geral, especialmente em regiões escuras/clipped.

### ✅ **Visualização do histograma**
Plota a distribuição de intensidades com `matplotlib`, fornecendo base para aplicar thresholds manuais ou entender o comportamento da imagem.

### ✅ **Threshold (binarização)**
Opção de definir um intervalo de intensidade (limiar esquerdo e direito).
- É aplicado com `np.where(...)`, gerando imagem binária personalizada.

### ✅ **Filtros**
Aplica dois filtros clássicos:
- **Gaussian Blur**: suaviza a imagem usando distribuição normal 2D;
- **Filtro da Mediana**: remove ruídos impulsivos (ex: sal e pimenta), preservando bordas.

### ✅ **Operações Morfológicas**
Usa `cv2.morphologyEx` e `cv2.dilate` para:
- **Abertura** (remoção de ruídos pequenos);
- **Dilatação** (expansão de regiões brancas).

Usa kernel elíptico (5x5) para preservar formas arredondadas como letras.

### ✅ **Segmentação com Watershed**
- Aplica `cv2.distanceTransform` e `cv2.connectedComponents` para identificar regiões seguras de fundo e frente.
- Usa `cv2.watershed()` para encontrar as bordas entre as regiões.
- Contornos são desenhados em vermelho na imagem original.
- A segmentação depende fortemente da equalização anterior para funcionar.

---

## 📆 Requisitos

Instale as dependências com:
```bash
pip install opencv-python numpy matplotlib
```
Para interface GUI:
```bash
# Em sistemas baseados em Debian/Ubuntu
sudo apt-get install python3-tk
```

---

## 📁 Estrutura do Projeto

```
ProjetoFinal_PDI/
├── interface.py         # Interface Tkinter com seleção modular de etapas junto com codigo do projeto
├── IMG_20250323_0002.jpg    # Imagem exemplo
├── README.md
├── Etapa2_ModelagemFuncionalDoSistema.pdf
```

---

## ▶️ Como Executar

### Modo Terminal (sem GUI):
```bash
python3 main.py
```

### Modo Gráfico com Interface Tkinter:
```bash
python3 interface.py
```

Na interface gráfica, o usuário pode:
- Selecionar uma imagem;
- Marcar uma ROI com 4 cliques;
- Aplicar as etapas desejadas de forma modular;
- Visualizar os resultados em janelas OpenCV.

---

## 📅 Observações

- Suporta imagens .jpg, .png, .bmp, etc.
- A ROI deve conter 4 cliques (cantos da região de interesse).
- O programa mostra mensagens de erro e interrompe execução em casos inválidos.
- O processamento não é destrutivo: a imagem original permanece intacta.

---

## 📄 Licença

Projeto acadêmico desenvolvido como parte da disciplina de Processamento Digital de Imagens da UFABC. Uso livre para fins educacionais e não comerciais.

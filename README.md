# ProjetoFinal_PDI

Projeto da disciplina de **Processamento Digital de Imagens (PDI)** - UFABC

- Leonardo Pires de Oliveira - 11201920744  
- Leonardo Fabiano de Souza - 11201721317  
- Murilo Valentim Alves - 11202130884  
- Stephany Caroline C. Santanna - 11201920287
---

## 🧠 Objetivo do Projeto

O intuito da aplicação é **realçar letras ou conteúdos que estão quase ilegíveis** em documentos, componentes eletrônicos ou superfícies diversas — com o objetivo de **facilitar a leitura ou análise visual** desses elementos.  

A aplicação permite ao usuário aplicar uma série de técnicas de PDI de forma interativa, visual e intuitiva.

---

## 🧰 Funcionalidades

- Seleção de **Região de Interesse (ROI)** com transformação por perspectiva;
- Conversão para **escala de cinza** e **equalização de histograma**;
- Visualização do histograma e **seleção de pixel** de referência;
- Aplicação de **threshold** (automático via derivada ou valores manuais);
- Aplicação de **filtros** (Gaussian Blur e Mediana);
- **Operações morfológicas**: abertura e dilatação;
- **Segmentação via Watershed**;
- Interface interativa via **terminal** ou **Tkinter (GUI)**.

---

## 📦 Requisitos

Instale as dependências com:

```bash
pip install opencv-python numpy matplotlib
```

Para usar a interface gráfica, o `tkinter` precisa estar instalado:

### Linux (Debian/Ubuntu):
```bash
sudo apt-get install python3-tk
```

---

## 📁 Estrutura do Projeto

```
ProjetoFinal_PDI/
├── main.py              # Script principal
├── interface.py         # Interface gráfica (Tkinter)
├── IMG_2025XXXXX.jpg    # Imagem de exemplo (apenas para testes iniciais)
├── README.md
```
---

## ▶️ Como Executar

### Modo Terminal (CLI):
```bash
python3 main.py
```

### Modo Interface Gráfica (GUI):
```bash
python3 interface.py
```

Na interface, o usuário pode:
- Selecionar imagem;
- Marcar ROI com 4 cliques;
- Aplicar etapas do processamento de forma modular;
- Visualizar cada etapa com `OpenCV`.

---

## 📌 Observações

- As imagens podem estar em formatos `.jpg`, `.png`, `.bmp`, etc.
- A ROI é obrigatoriamente selecionada com **4 pontos**.
- Em caso de clique inválido, a aplicação será interrompida com aviso.
- A aplicação foi projetada para ser simples e rápida de testar.

---

## 📄 Licença

Este projeto foi desenvolvido como parte da disciplina de Processamento Digital de Imagens da UFABC. Uso acadêmico e não comercial.

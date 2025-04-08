import os
import shutil
import hashlib
import tkinter.filedialog as fd
from PIL import Image, ImageTk
import customtkinter as ctk
from tkinter import messagebox
import threading
import sys

# ========== Suporte ao logo mesmo após empacotar com PyInstaller ==========
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ========== Funções de otimização ==========
def otimizar_imagem(caminho_entrada, caminho_saida, qualidade=70, tamanho_max=(1024, 1024)):
    try:
        with Image.open(caminho_entrada) as img:
            img.thumbnail(tamanho_max)
            img.save(caminho_saida, optimize=True, quality=qualidade)
    except Exception as e:
        print(f"Erro ao otimizar imagem {caminho_entrada}: {e}")

def hash_imagem(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def detectar_imagens_duplicadas(pasta):
    hashes = {}
    duplicatas = []
    for root, _, arquivos in os.walk(pasta):
        for nome_arquivo in arquivos:
            caminho = os.path.join(root, nome_arquivo)
            if caminho.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                h = hash_imagem(caminho)
                if h in hashes:
                    duplicatas.append(caminho)
                else:
                    hashes[h] = caminho
    return duplicatas

def processar_imagens(caminhos):
    total = len(caminhos)
    for i, caminho in enumerate(caminhos, start=1):
        nome_arquivo = os.path.basename(caminho)
        destino = os.path.join("imagens_otimizadas", nome_arquivo)
        shutil.copy2(caminho, os.path.join("imagens_original", nome_arquivo))
        otimizar_imagem(caminho, destino)
        progresso.set(i / total * 100)
        app.update_idletasks()
    duplicatas = detectar_imagens_duplicadas("imagens_otimizadas")
    for dup in duplicatas:
        os.remove(dup)
    messagebox.showinfo("Concluído", f"Otimização finalizada!\nImagens duplicadas removidas: {len(duplicatas)}")

def iniciar_otimizacao(caminhos):
    if not caminhos:
        messagebox.showwarning("Aviso", "Nenhuma imagem selecionada.")
        return
    os.makedirs("imagens_original", exist_ok=True)
    os.makedirs("imagens_otimizadas", exist_ok=True)
    threading.Thread(target=processar_imagens, args=(caminhos,)).start()

# ========== Interface gráfica ==========
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Otimizador de Imagens")
app.geometry("500x600")
app.resizable(False, False)

# LOGO
logo_path = resource_path("logo.png")
logo_img = Image.open(logo_path)
logo_img = logo_img.resize((120, 120))
logo_ctk = ctk.CTkImage(light_image=logo_img, size=(120, 120))
logo_label = ctk.CTkLabel(app, image=logo_ctk, text="")
logo_label.pack(pady=10)

ctk.CTkLabel(app, text="Otimizador de Imagens", font=("Arial", 22, "bold")).pack(pady=5)
ctk.CTkLabel(app, text="Escolha uma pasta ou arquivos de imagem para otimizar.", wraplength=400).pack(pady=5)

def escolher_arquivo():
    arquivos = fd.askopenfilenames(filetypes=[("Imagens", "*.png *.jpg *.jpeg *.webp")])
    iniciar_otimizacao(list(arquivos))

def escolher_pasta():
    pasta = fd.askdirectory()
    if pasta:
        imagens = [os.path.join(pasta, f) for f in os.listdir(pasta)
                   if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        iniciar_otimizacao(imagens)

ctk.CTkButton(app, text="Escolher Arquivos", command=escolher_arquivo).pack(pady=10)
ctk.CTkButton(app, text="Escolher Pasta", command=escolher_pasta).pack(pady=5)

progresso = ctk.CTkProgressBar(app, width=400)
progresso.set(0)
progresso.pack(pady=30)

ctk.CTkLabel(app, text="© Soma Soluções").pack(side="bottom", pady=10)

app.mainloop()

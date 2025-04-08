import os
import sys
import shutil
import hashlib
import threading
import io
from PIL import Image, ImageTk
import customtkinter as ctk
from tkinter import messagebox, filedialog

# Suporte a recursos mesmo com PyInstaller
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Redimensiona imagem mantendo proporção e respeitando limites
def redimensionar(img):
    largura, altura = img.size

    # Aumentar se menor que 1000x1000
    if largura < 1000 or altura < 1000:
        escala = max(1000 / largura, 1000 / altura)
        nova = (int(largura * escala), int(altura * escala))
        img = img.resize(nova, Image.LANCZOS)

    # Reduzir se maior que 2000x2000
    if img.width > 2000 or img.height > 2000:
        escala = min(2000 / img.width, 2000 / img.height)
        nova = (int(img.width * escala), int(img.height * escala))
        img = img.resize(nova, Image.LANCZOS)

    # Garante mínimo absoluto
    largura, altura = img.size
    nova_largura = max(largura, 1000)
    nova_altura = max(altura, 1000)
    if nova_largura != largura or nova_altura != altura:
        img = img.resize((nova_largura, nova_altura), Image.LANCZOS)

    return img

# Otimiza a imagem para o tamanho máximo em KB
def otimizar_imagem(caminho_entrada, caminho_saida, tamanho_max_kb=350):
    try:
        with Image.open(caminho_entrada) as img:
            img = redimensionar(img)

            # Converte para RGB se necessário
            if img.mode != "RGB":
                img = img.convert("RGB")

            qualidade = 95
            while qualidade >= 10:
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", optimize=True, quality=qualidade)
                size_kb = buffer.tell() / 1024
                if size_kb <= tamanho_max_kb:
                    with open(caminho_saida, "wb") as f:
                        f.write(buffer.getvalue())
                    return
                qualidade -= 5

            messagebox.showwarning("Atenção", f"A imagem '{os.path.basename(caminho_entrada)}' não pôde ser reduzida para menos de {tamanho_max_kb}KB.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao otimizar imagem:\n{e}")

# Calcula hash para detectar duplicatas
def hash_imagem(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

# Remove duplicatas da pasta destino
def remover_duplicatas(pasta_destino):
    hashes = {}
    duplicatas = []
    for root, _, arquivos in os.walk(pasta_destino):
        for nome_arquivo in arquivos:
            caminho = os.path.join(root, nome_arquivo)
            if caminho.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                h = hash_imagem(caminho)
                if h in hashes:
                    duplicatas.append(caminho)
                else:
                    hashes[h] = caminho
    for dup in duplicatas:
        os.remove(dup)
    return len(duplicatas)

# Processa as imagens
def processar_imagens(caminhos, pasta_destino):
    total = len(caminhos)
    for i, caminho in enumerate(caminhos, start=1):
        nome_arquivo = os.path.basename(caminho)
        destino = os.path.join(pasta_destino, f"{os.path.splitext(nome_arquivo)[0]}.jpg")

        otimizar_imagem(caminho, destino)
        progresso.set(i / total * 100)
        app.update_idletasks()

    removidas = remover_duplicatas(pasta_destino)
    messagebox.showinfo("Concluído", f"Otimização finalizada!\nImagens duplicadas removidas: {removidas}")

# Thread segura
def iniciar_otimizacao(caminhos):
    if not caminhos:
        messagebox.showwarning("Aviso", "Nenhuma imagem selecionada.")
        return
    pasta_destino = filedialog.askdirectory(title="Escolha a pasta de destino")
    if not pasta_destino:
        return
    threading.Thread(target=processar_imagens, args=(caminhos, pasta_destino)).start()

# ========== Interface Gráfica ========== #
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Otimizador de Imagens")
app.geometry("500x600")
app.resizable(False, False)

# Logo (opcional)
try:
    logo_path = resource_path("logo.png")
    logo_img = Image.open(logo_path).resize((120, 120))
    logo_ctk = ctk.CTkImage(light_image=logo_img, size=(120, 120))
    logo_label = ctk.CTkLabel(app, image=logo_ctk, text="")
    logo_label.pack(pady=10)
except:
    pass

ctk.CTkLabel(app, text="Otimizador de Imagens", font=("Arial", 22, "bold")).pack(pady=5)
ctk.CTkLabel(app, text="Escolha imagens ou uma pasta para otimizar.\nApós isso, escolha a pasta de destino.",
             wraplength=400, justify="center").pack(pady=5)

def escolher_arquivos():
    arquivos = filedialog.askopenfilenames(filetypes=[("Imagens", "*.png *.jpg *.jpeg *.webp")])
    iniciar_otimizacao(list(arquivos))

def escolher_pasta():
    pasta = filedialog.askdirectory()
    if pasta:
        imagens = [os.path.join(pasta, f) for f in os.listdir(pasta)
                   if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        iniciar_otimizacao(imagens)

ctk.CTkButton(app, text="Escolher Arquivos", command=escolher_arquivos).pack(pady=10)
ctk.CTkButton(app, text="Escolher Pasta", command=escolher_pasta).pack(pady=5)

progresso = ctk.CTkProgressBar(app, width=400)
progresso.set(0)
progresso.pack(pady=30)

ctk.CTkLabel(app, text="© Soma Soluções").pack(side="bottom", pady=10)

app.mainloop()

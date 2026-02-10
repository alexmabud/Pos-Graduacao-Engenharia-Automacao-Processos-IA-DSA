# Projeto 2 - Automação do Processo de Backup, Movimentação de Arquivos, Criptografia e Logging com Python
# Script Versão 4 - Parte 2

# Imports
import os
import shutil
import zipfile
import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet

# Função para descompactar o arquivo zip
def descompactar_arquivo_zip(arquivo_zip, diretorio_destino):
    with zipfile.ZipFile(arquivo_zip, 'r') as zip_ref:
        zip_ref.extractall(diretorio_destino)

# Função para descriptografar os arquivos CSV
def descriptografar_arquivos_csv(diretorio, chave):
    cipher_suite = Fernet(chave)
    for arquivo in os.listdir(diretorio):
        if arquivo.endswith(".csv"):
            caminho_arquivo = os.path.join(diretorio, arquivo)
            with open(caminho_arquivo, 'rb') as f:
                conteudo_criptografado = f.read()
            conteudo_descriptografado = cipher_suite.decrypt(conteudo_criptografado)
            with open(caminho_arquivo, 'wb') as f:
                f.write(conteudo_descriptografado)

# Função para exibir um popup com uma mensagem.
def dsa_exibe_popup(mensagem, sucesso=True):
    root = tk.Tk()
    root.withdraw()
    if sucesso:
        messagebox.showinfo("Sucesso", mensagem)
    else:
        messagebox.showerror("Erro", mensagem)

# Função principal do projeto 2.
def dsaprojeto2():

    # Diretório onde o arquivo zip de backup está localizado
    diretorio_arquivo = "/Users/dmpm/Dropbox/DSA4.0/Automation-Python-Excel-IA/Cap07/destino"

    # Diretório onde os arquivos serão extraídos
    diretorio_final = "/Users/dmpm/Dropbox/DSA4.0/Automation-Python-Excel-IA/Cap07/destino/final"
    
    # Arquivo onde a chave de criptografia está armazenada
    chave_arquivo = "chave.key"

    # Procurar o primeiro arquivo ZIP encontrado na pasta de origem
    arquivo_zip = next((os.path.join(diretorio_arquivo, f) for f in os.listdir(diretorio_arquivo) if f.endswith('.zip')), None)

    if not arquivo_zip:
        print("Nenhum arquivo zip foi encontrado na pasta de origem.")
        return

    # Criar diretório de destino se não existir
    if not os.path.exists(diretorio_final):
        os.makedirs(diretorio_final)

    # Carregar a chave de criptografia do arquivo
    with open(chave_arquivo, 'rb') as f:
        chave = f.read()

    # Descompactar o arquivo zip de backup
    descompactar_arquivo_zip(arquivo_zip, diretorio_final)
    dsa_exibe_popup("Descompactação concluída com sucesso!")

    # Descriptografar os arquivos CSV no diretório de destino
    descriptografar_arquivos_csv(diretorio_final, chave)
    dsa_exibe_popup("Descriptografia concluída com sucesso!")

if __name__ == "__main__":
    dsaprojeto2()

# Projeto 2 - Automação do Processo de Backup, Movimentação de Arquivos, Criptografia e Logging com Python
# Script Versão 3

# Imports
import os
import shutil
import zipfile
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from cryptography.fernet import Fernet

# Chave para criptografia
chave = Fernet.generate_key()
cipher_suite = Fernet(chave)

# Função para buscar arquivos CSV em um diretório específico.
def dsa_busca_arquivos_csv(diretorio):

    # Lista para armazenar os caminhos dos arquivos CSV encontrados.
    arquivos_csv = []

    # Percorre recursivamente o diretório especificado e seus subdiretórios.
    for root, dirs, files in os.walk(diretorio):

        # Percorre todos os arquivos no diretório atual.
        for file in files:

            # Verifica se o arquivo possui a extensão .csv
            if file.endswith(".csv"):

                # Adiciona o caminho completo do arquivo à lista de arquivos CSV.
                arquivos_csv.append(os.path.join(root, file))

    # Retorna a lista de caminhos dos arquivos CSV encontrados.
    return arquivos_csv

# Função para compactar uma lista de arquivos em um arquivo zip.
def dsa_compacta_arquivos(arquivos, origem):
    
    # Abre um arquivo zip para escrita.
    with zipfile.ZipFile(origem, 'w') as zipf:
        
        # Itera sobre cada arquivo na lista de arquivos fornecida.
        for arquivo in arquivos:
            
            # Abre o arquivo atual no modo de leitura binária ('rb').
            with open(arquivo, 'rb') as f:
                
                # Lê o conteúdo do arquivo.
                conteudo = f.read()
                
                # Criptografa o conteúdo do arquivo usando o cipher_suite.
                conteudo_criptografado = cipher_suite.encrypt(conteudo)
            
            # Obtém o nome base do arquivo (sem o caminho).
            nome_arquivo = os.path.basename(arquivo)
            
            # Escreve o conteúdo criptografado no arquivo ZIP usando o nome base do arquivo.
            zipf.writestr(nome_arquivo, conteudo_criptografado)

# Função para mover um arquivo de uma localização de origem para uma localização de destino.
def dsa_move_arquivo(origem, destino):
    if not os.path.exists(destino):
        os.makedirs(destino)
    shutil.move(origem, destino)

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

    # Diretórios
    diretorio_fonte = "/Users/dmpm/Dropbox/DSA4.0/Automation-Python-Excel-IA/Cap07/origem"
    diretorio_destino = "/Users/dmpm/Dropbox/DSA4.0/Automation-Python-Excel-IA/Cap07/destino"
    
    # Busca por arquivos CSV no diretório de origem.
    arquivos_csv = dsa_busca_arquivos_csv(diretorio_fonte)
    
    # Verifica se foram encontrados arquivos CSV.
    if not arquivos_csv:
        dsa_exibe_popup("Nenhum arquivo CSV encontrado.", sucesso=False)
        return
    
    # Nome do arquivo zip para o backup.
    nome_zip = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

    # Caminho completo para o arquivo zip.
    caminho_zip = os.path.join(diretorio_fonte, nome_zip)
    
    # Bloco try/except
    try:
        dsa_compacta_arquivos(arquivos_csv, caminho_zip)
        dsa_exibe_popup("Compactação e criptografia concluídos com sucesso!")
    except Exception as e:
        dsa_exibe_popup(f"Erro durante Compactação e Criptografia: {str(e)}", sucesso=False)

    # Bloco try/except
    try:
        dsa_move_arquivo(caminho_zip, diretorio_destino)
        dsa_exibe_popup("Movimentação do arquivo concluída com sucesso!")
    except Exception as e:
        dsa_exibe_popup(f"Erro durante o backup: {str(e)}", sucesso=False)

if __name__ == "__main__":
    dsaprojeto2()

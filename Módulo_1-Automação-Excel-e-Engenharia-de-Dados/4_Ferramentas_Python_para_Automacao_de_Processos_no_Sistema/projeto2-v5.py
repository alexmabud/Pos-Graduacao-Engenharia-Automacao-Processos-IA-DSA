# Projeto 2 - Automação do Processo de Backup, Movimentação de Arquivos, Criptografia e Logging com Python
# Script Versão 5

# Imports
import os
import shutil
import zipfile
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
from cryptography.fernet import Fernet
import platform
import getpass

# Função para salvar a chave em um arquivo
def dsa_salva_chave(chave, nome_arquivo):
    with open(nome_arquivo, 'wb') as f:
        f.write(chave)

# Função para carregar a chave do arquivo
def dsa_carrega_chave(nome_arquivo):
    with open(nome_arquivo, 'rb') as f:
        return f.read()

# Verifica se a chave já foi gerada anteriormente
nome_arquivo_chave = 'chave.key'
if not os.path.exists(nome_arquivo_chave):
    chave = Fernet.generate_key()
    dsa_salva_chave(chave, nome_arquivo_chave)
else:
    chave = dsa_carrega_chave(nome_arquivo_chave)

# Cria o objeto Fernet com a chave carregada
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
    with zipfile.ZipFile(origem, 'w') as zipf:
        for arquivo in arquivos:
            with open(arquivo, 'rb') as f:
                conteudo = f.read()
                conteudo_criptografado = cipher_suite.encrypt(conteudo)
            nome_arquivo = os.path.basename(arquivo)
            zipf.writestr(nome_arquivo, conteudo_criptografado)

# Função para mover um arquivo de uma localização de origem para uma localização de destino.
def dsa_move_arquivo(origem, destino):
    if not os.path.exists(destino):
        os.makedirs(destino)
    shutil.move(origem, destino)

# Função para exibir um popup com uma mensagem.
def dsa_exibe_popup(mensagem, sucesso=True):
    if sucesso:
        messagebox.showinfo("Sucesso", mensagem)
    else:
        messagebox.showerror("Erro", mensagem)

# Função para gerar arquivo de log com detalhes do sistema
def dsa_gera_log():
    nome_arquivo_log = 'log.txt'
    usuario = getpass.getuser()
    with open(nome_arquivo_log, 'w') as f:
        f.write(f"Detalhes do Sistema:\n\n")
        f.write(f"Sistema Operacional: {platform.system()}\n")
        f.write(f"Versão do Sistema: {platform.version()}\n")
        f.write(f"Arquitetura do Sistema: {platform.architecture()}\n")
        f.write(f"Nome do Computador: {platform.node()}\n")
        f.write(f"Plataforma: {platform.platform()}\n")
        f.write(f"Usuário: {usuario}\n")

# Função para o usuário selecionar a pasta de origem
def selecionar_diretorio_origem():
    diretorio_origem = filedialog.askdirectory(title="Selecionar Diretório de Origem")
    if diretorio_origem:
        diretorio_destino = "/Users/dmpm/Dropbox/DSA4.0/Automation-Python-Excel-IA/Cap07/destino"
        dsa_realizar_backup(diretorio_origem, diretorio_destino)

# Função para executar o backup
def dsa_realizar_backup(diretorio_origem, diretorio_destino):

    # Busca por arquivos CSV no diretório de origem.
    arquivos_csv = dsa_busca_arquivos_csv(diretorio_origem)
    
    # Verifica se foram encontrados arquivos CSV.
    if not arquivos_csv:
        dsa_exibe_popup("Nenhum arquivo CSV encontrado.", sucesso=False)
        return
    
    # Nome do arquivo zip para o backup.
    nome_zip = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

    # Caminho completo para o arquivo zip.
    caminho_zip = os.path.join(diretorio_destino, nome_zip)
    
    # Bloco try/except
    try:
        dsa_compacta_arquivos(arquivos_csv, caminho_zip)
        dsa_exibe_popup("Backup concluído com sucesso!")
        dsa_gera_log()
    except Exception as e:
        dsa_exibe_popup(f"Erro durante o backup: {str(e)}", sucesso=False)

# Função principal do projeto 2.
def dsap2():

    # Cria os objetos
    root = tk.Tk()
    root.withdraw()
    
    # Criar janela principal
    janela_principal = tk.Toplevel(root)
    janela_principal.title("Backup de Arquivos")
    
    # Botão para selecionar o diretório de origem
    botao_selecionar = tk.Button(janela_principal, text="Selecionar Diretório de Origem", command=selecionar_diretorio_origem)
    botao_selecionar.pack()

    # Definir ação a ser executada ao fechar a janela
    janela_principal.protocol("WM_DELETE_WINDOW", root.quit)

    root.mainloop()

if __name__ == "__main__":
    dsap2()

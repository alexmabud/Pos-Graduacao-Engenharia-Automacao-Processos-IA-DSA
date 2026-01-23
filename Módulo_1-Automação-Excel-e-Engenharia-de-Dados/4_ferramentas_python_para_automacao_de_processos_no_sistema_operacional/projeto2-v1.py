# Projeto 2 - Automação do Processo de Backup, Movimentação de Arquivos, Criptografia e Logging com Python
# Script Versão 1

# Imports
import os
import shutil
import zipfile
import tkinter as tk
from tkinter import messagebox

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

        # Percorre cada arquivo na lista de arquivos.
        for arquivo in arquivos:

            # Adiciona o arquivo ao arquivo zip, mantendo apenas o nome do arquivo.
            zipf.write(arquivo, os.path.basename(arquivo))

# Função para mover um arquivo de uma localização de origem para uma localização de destino.
def dsa_move_arquivo(origem, destino):

    # Verifica se o diretório de destino existe; se não, cria o diretório.
    if not os.path.exists(destino):
        os.makedirs(destino)

    # Move o arquivo da origem para o destino.
    shutil.move(origem, destino)

# Função para exibir um popup com uma mensagem.
def dsa_exibe_popup(mensagem, sucesso=True):

    # Cria uma instância da classe Tk para a janela.
    root = tk.Tk()

    # Esconde a janela principal.
    root.withdraw()

    # Verifica se a mensagem é de sucesso ou erro e exibe o popup correspondente.
    if sucesso:
        # Exibe um popup de informação com a mensagem de sucesso.
        messagebox.showinfo("Sucesso", mensagem)
    else:
        # Exibe um popup de erro com a mensagem de erro.
        messagebox.showerror("Erro", mensagem)

# Função principal do projeto 2.
def dsaprojeto2():

    # Diretório de onde os arquivos serão copiados.
    diretorio_fonte = "/Users/dmpm/Dropbox/DSA4.0/Automation-Python-Excel-IA/Cap07/origem"

    # Diretório para onde os arquivos serão movidos.
    diretorio_destino = "/Users/dmpm/Dropbox/DSA4.0/Automation-Python-Excel-IA/Cap07/destino"
    
    # Busca por arquivos CSV no diretório de origem.
    arquivos_csv = dsa_busca_arquivos_csv(diretorio_fonte)
    
    # Verifica se foram encontrados arquivos CSV.
    if not arquivos_csv:
        # Exibe um popup informando que nenhum arquivo CSV foi encontrado.
        dsa_exibe_popup("Nenhum arquivo CSV encontrado.", sucesso=False)
        return
    
    # Nome do arquivo zip para o backup.
    nome_zip = "backup.zip"

    # Caminho completo para o arquivo zip.
    caminho_zip = os.path.join(diretorio_fonte, nome_zip)
    
    # Bloco try/except
    try:
        
        # Compacta os arquivos CSV em um arquivo zip.
        dsa_compacta_arquivos(arquivos_csv, caminho_zip)
        
        # Move o arquivo zip compactado para o diretório de destino.
        dsa_move_arquivo(caminho_zip, diretorio_destino)
        
        # Exibe um popup informando que o backup foi concluído com sucesso.
        dsa_exibe_popup("Backup concluído com sucesso!")
    
    except Exception as e:
        
        # Em caso de erro, exibe um popup informando o erro ocorrido.
        dsa_exibe_popup(f"Erro durante o backup: {str(e)}", sucesso=False)

# Verifica se o arquivo está sendo executado como o programa principal.
if __name__ == "__main__":

    # Chama a função principal do projeto 2.
    dsaprojeto2()


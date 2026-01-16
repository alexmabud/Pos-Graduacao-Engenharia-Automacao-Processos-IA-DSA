# Projeto 2 - Automação do Processo de Backup, Movimentação de Arquivos, Criptografia e Logging com Python
# Script Versão Completa - Backup, Restore e Interface Gráfica

# ==========================================
# IMPORTS
# ==========================================
import os
import shutil
import zipfile
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
from cryptography.fernet import Fernet
import platform
import getpass


# ==========================================
# CONFIGURAÇÃO DE CAMINHOS (Constantes)
# ==========================================
# Base: Diretório principal do Módulo 1
CAMINHO_BASE = r"C:\Users\User\OneDrive\Documentos\Python\Dev_Python\Abud Python Learning\DSA\Módulo_1-Automação-Excel-e-Engenharia-de-Dados\4_Ferramentas_Python_para_Automacao_de_Processos_no_Sistema"

# Origem: Onde os arquivos brutos chegam
CAMINHO_ORIGEM = os.path.join(CAMINHO_BASE, "origem")

# Destino: Para onde os arquivos processados/organizados vão
CAMINHO_DESTINO = os.path.join(CAMINHO_BASE, "destino")

# Final: Onde os arquivos restaurados ficam
CAMINHO_FINAL = os.path.join(CAMINHO_BASE, "destino", "final")


# ==========================================
# CRIPTOGRAFIA - SETUP
# ==========================================
# Função para salvar a chave em um arquivo
def dsa_salva_chave(chave, nome_arquivo):
    with open(nome_arquivo, 'wb') as f:
        f.write(chave)

# Função para carregar a chave do arquivo
def dsa_carrega_chave(nome_arquivo):
    with open(nome_arquivo, 'rb') as f:
        return f.read()

# Verifica se a chave já foi gerada anteriormente
nome_arquivo_chave = os.path.join(CAMINHO_BASE, 'chave.key')
if not os.path.exists(nome_arquivo_chave):
    chave = Fernet.generate_key()
    dsa_salva_chave(chave, nome_arquivo_chave)
else:
    chave = dsa_carrega_chave(nome_arquivo_chave)

# Criar o objeto Fernet com a chave carregada
cipher_suite = Fernet(chave)


# ==========================================
# FUNÇÕES DE BACKUP
# ==========================================
# Função para buscar arquivos CSV em um diretório específico.
def dsa_busca_arquivos_csv(diretorio):
    arquivos_csv = []
    for root, dirs, files in os.walk(diretorio):
        for file in files:
            if file.endswith(".csv"):
                arquivos_csv.append(os.path.join(root, file))
    return arquivos_csv

# Função para compactar uma lista de arquivos em um arquivo zip com criptografia.
def dsa_compacta_arquivos(arquivos, caminho_zip):
    # Abre um arquivo zip para escrita.
    with zipfile.ZipFile(caminho_zip, 'w') as zipf:
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

# Função para mover um arquivo de um local para outro.
def dsa_move_arquivo(origem, destino):
    # Cria a pasta de destino se ela não existir
    if not os.path.exists(destino):
        os.makedirs(destino)
    # Move o arquivo da origem para o destino.
    shutil.move(origem, destino)


# ==========================================
# FUNÇÕES DE RESTORE
# ==========================================
# Função para descompactar o arquivo zip
def descompactar_arquivo_zip(arquivo_zip, diretorio_destino):
    with zipfile.ZipFile(arquivo_zip, 'r') as zip_ref:
        zip_ref.extractall(diretorio_destino)

# Função para descriptografar os arquivos CSV
def descriptografar_arquivos_csv(diretorio):
    for arquivo in os.listdir(diretorio):
        if arquivo.endswith(".csv"):
            caminho_arquivo = os.path.join(diretorio, arquivo)
            with open(caminho_arquivo, 'rb') as f:
                conteudo_criptografado = f.read()
            conteudo_descriptografado = cipher_suite.decrypt(conteudo_criptografado)
            with open(caminho_arquivo, 'wb') as f:
                f.write(conteudo_descriptografado)


# ==========================================
# FUNÇÕES DE LOGGING
# ==========================================
# Função para gerar arquivo de log com detalhes do sistema
def dsa_gera_log():
    # Salva o log no diretório base do Módulo 1
    nome_arquivo_log = os.path.join(CAMINHO_BASE, 'log.txt')
    usuario = getpass.getuser()
    with open(nome_arquivo_log, 'w') as f:
        f.write(f"Detalhes do Sistema:\n\n")
        f.write(f"Sistema Operacional: {platform.system()}\n")
        f.write(f"Versão do Sistema: {platform.version()}\n")
        f.write(f"Arquitetura do Sistema: {platform.architecture()}\n")
        f.write(f"Nome do Computador: {platform.node()}\n")
        f.write(f"Plataforma: {platform.platform()}\n")
        f.write(f"Usuário: {usuario}\n")
        f.write(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


# ==========================================
# FUNÇÕES UTILITÁRIAS (UI)
# ==========================================
# Função para exibir popups de sucesso ou erro.
def dsa_exibe_popup(mensagem, sucesso=True):
    root = tk.Tk()
    root.withdraw()
    if sucesso:
        messagebox.showinfo("Sucesso", mensagem)
    else:
        messagebox.showerror("Erro", mensagem)
    root.destroy()


# ==========================================
# FUNÇÕES PRINCIPAIS (Console)
# ==========================================
# Função para realizar o backup (via console)
def fazer_backup_console():
    print("\n=== INICIANDO BACKUP ===")

    # 1. Busca por arquivos CSV no diretório de origem.
    arquivos_csv = dsa_busca_arquivos_csv(CAMINHO_ORIGEM)

    # 2. Verifica se foram encontrados arquivos CSV
    if not arquivos_csv:
        dsa_exibe_popup("Nenhum arquivo CSV encontrado.", sucesso=False)
        print("❌ Nenhum arquivo CSV encontrado.")
        return

    print(f"✅ {len(arquivos_csv)} arquivo(s) CSV encontrado(s).")

    # 3. Nome e caminho do arquivo zip com timestamp
    nome_zip = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    caminho_zip = os.path.join(CAMINHO_ORIGEM, nome_zip)

    # 4. Bloco try/except para compactação e criptografia
    try:
        print("🔐 Iniciando compactação e criptografia...")
        dsa_compacta_arquivos(arquivos_csv, caminho_zip)
        dsa_exibe_popup("Compactação e criptografia concluídos com sucesso!")
        print("✅ Compactação e criptografia concluídas!")
    except Exception as e:
        dsa_exibe_popup(f"Erro durante Compactação e Criptografia: {str(e)}", sucesso=False)
        print(f"❌ Erro: {str(e)}")
        return

    # 5. Bloco try/except para movimentação
    try:
        print("📦 Movendo backup para o destino...")
        dsa_move_arquivo(caminho_zip, CAMINHO_DESTINO)
        dsa_exibe_popup("Movimentação do arquivo concluída com sucesso!")
        print(f"✅ Backup movido para: {CAMINHO_DESTINO}")
    except Exception as e:
        dsa_exibe_popup(f"Erro durante a movimentação: {str(e)}", sucesso=False)
        print(f"❌ Erro na movimentação: {str(e)}")
        return

    # 6. Gera log do sistema
    try:
        dsa_gera_log()
        print("📝 Log do sistema gerado: log.txt")
    except Exception as e:
        print(f"⚠️ Aviso: Não foi possível gerar o log: {str(e)}")

    print("=== BACKUP CONCLUÍDO COM SUCESSO ===\n")

# Função para restaurar o backup (via console)
def restaurar_backup_console():
    print("\n=== INICIANDO RESTORE ===")

    # 1. Procurar o primeiro arquivo ZIP encontrado na pasta de destino
    try:
        arquivo_zip = next((os.path.join(CAMINHO_DESTINO, f) for f in os.listdir(CAMINHO_DESTINO) if f.endswith('.zip')), None)
    except FileNotFoundError:
        dsa_exibe_popup(f"Diretório não encontrado: {CAMINHO_DESTINO}", sucesso=False)
        print(f"❌ Diretório não encontrado: {CAMINHO_DESTINO}")
        return

    if not arquivo_zip:
        dsa_exibe_popup("Nenhum arquivo zip foi encontrado na pasta de destino.", sucesso=False)
        print("❌ Nenhum arquivo ZIP encontrado.")
        return

    print(f"✅ Arquivo ZIP encontrado: {os.path.basename(arquivo_zip)}")

    # 2. Criar diretório final se não existir
    if not os.path.exists(CAMINHO_FINAL):
        os.makedirs(CAMINHO_FINAL)
        print(f"📁 Diretório criado: {CAMINHO_FINAL}")

    # 3. Bloco try/except para descompactação
    try:
        print("📦 Descompactando arquivo...")
        descompactar_arquivo_zip(arquivo_zip, CAMINHO_FINAL)
        dsa_exibe_popup("Descompactação concluída com sucesso!")
        print("✅ Descompactação concluída!")
    except Exception as e:
        dsa_exibe_popup(f"Erro durante a descompactação: {str(e)}", sucesso=False)
        print(f"❌ Erro: {str(e)}")
        return

    # 4. Bloco try/except para descriptografia
    try:
        print("🔓 Descriptografando arquivos CSV...")
        descriptografar_arquivos_csv(CAMINHO_FINAL)
        dsa_exibe_popup("Descriptografia concluída com sucesso!")
        print("✅ Descriptografia concluída!")
    except Exception as e:
        dsa_exibe_popup(f"Erro durante a descriptografia: {str(e)}", sucesso=False)
        print(f"❌ Erro: {str(e)}")
        return

    print(f"✅ Arquivos restaurados em: {CAMINHO_FINAL}")
    print("=== RESTORE CONCLUÍDO COM SUCESSO ===\n")


# ==========================================
# FUNÇÕES PRINCIPAIS (Interface Gráfica)
# ==========================================
# Função para realizar backup com seleção de diretórios
def fazer_backup_interface():
    # Seleciona diretório de origem
    diretorio_origem = filedialog.askdirectory(title="Selecionar Diretório de Origem (onde estão os CSVs)")
    if not diretorio_origem:
        dsa_exibe_popup("Nenhum diretório de origem selecionado.", sucesso=False)
        return

    # Seleciona diretório de destino
    diretorio_destino = filedialog.askdirectory(title="Selecionar Diretório de Destino (onde salvar o backup)")
    if not diretorio_destino:
        dsa_exibe_popup("Nenhum diretório de destino selecionado.", sucesso=False)
        return

    # Busca por arquivos CSV no diretório de origem
    arquivos_csv = dsa_busca_arquivos_csv(diretorio_origem)

    # Verifica se foram encontrados arquivos CSV
    if not arquivos_csv:
        dsa_exibe_popup("Nenhum arquivo CSV encontrado no diretório selecionado.", sucesso=False)
        return

    # Nome do arquivo zip para o backup
    nome_zip = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

    # Caminho completo para o arquivo zip
    caminho_zip = os.path.join(diretorio_destino, nome_zip)

    # Bloco try/except
    try:
        dsa_compacta_arquivos(arquivos_csv, caminho_zip)
        dsa_gera_log()
        dsa_exibe_popup(f"Backup concluído com sucesso!\n\nArquivo: {nome_zip}\nLocal: {diretorio_destino}")
    except Exception as e:
        dsa_exibe_popup(f"Erro durante o backup: {str(e)}", sucesso=False)

# Função para restaurar backup com seleção de diretórios
def restaurar_backup_interface():
    # Seleciona o arquivo ZIP para restaurar
    arquivo_zip = filedialog.askopenfilename(
        title="Selecionar arquivo ZIP para restaurar",
        filetypes=[("Arquivos ZIP", "*.zip"), ("Todos os arquivos", "*.*")]
    )
    if not arquivo_zip:
        dsa_exibe_popup("Nenhum arquivo ZIP selecionado.", sucesso=False)
        return

    # Seleciona diretório de destino para os arquivos restaurados
    diretorio_final = filedialog.askdirectory(title="Selecionar Diretório para Restaurar os Arquivos")
    if not diretorio_final:
        dsa_exibe_popup("Nenhum diretório de destino selecionado.", sucesso=False)
        return

    # Criar diretório de destino se não existir
    if not os.path.exists(diretorio_final):
        os.makedirs(diretorio_final)

    # Bloco try/except para descompactação
    try:
        descompactar_arquivo_zip(arquivo_zip, diretorio_final)
    except Exception as e:
        dsa_exibe_popup(f"Erro durante a descompactação: {str(e)}", sucesso=False)
        return

    # Bloco try/except para descriptografia
    try:
        descriptografar_arquivos_csv(diretorio_final)
        dsa_exibe_popup(f"Restore concluído com sucesso!\n\nArquivos restaurados em:\n{diretorio_final}")
    except Exception as e:
        dsa_exibe_popup(f"Erro durante a descriptografia: {str(e)}", sucesso=False)


# ==========================================
# INTERFACE GRÁFICA PRINCIPAL
# ==========================================
def interface_grafica():
    # Função para fechar a interface e encerrar o programa
    def fechar_tudo():
        root.destroy()
        print("\n👋 Sistema encerrado pela interface gráfica.")
        exit()  # Encerra o programa completamente

    # Cria a janela principal
    root = tk.Tk()
    root.title("Sistema de Backup Criptografado - DSA")
    root.geometry("500x400")
    root.resizable(False, False)

    # Título
    titulo = tk.Label(root, text="Sistema de Backup Criptografado", font=("Arial", 16, "bold"), pady=20)
    titulo.pack()

    # Subtítulo
    subtitulo = tk.Label(root, text="Projeto 2 - Automação de Processos com Python", font=("Arial", 10), pady=5)
    subtitulo.pack()

    # Frame para os botões
    frame_botoes = tk.Frame(root, pady=20)
    frame_botoes.pack()

    # Botão: Fazer Backup
    btn_backup = tk.Button(
        frame_botoes,
        text="🔐 Fazer Backup",
        font=("Arial", 12, "bold"),
        width=30,
        height=2,
        bg="#4CAF50",
        fg="white",
        command=fazer_backup_interface
    )
    btn_backup.pack(pady=10)

    # Botão: Restaurar Backup
    btn_restore = tk.Button(
        frame_botoes,
        text="🔓 Restaurar Backup",
        font=("Arial", 12, "bold"),
        width=30,
        height=2,
        bg="#2196F3",
        fg="white",
        command=restaurar_backup_interface
    )
    btn_restore.pack(pady=10)

    # Botão: Sair
    btn_sair = tk.Button(
        frame_botoes,
        text="❌ Sair",
        font=("Arial", 12),
        width=30,
        height=2,
        bg="#f44336",
        fg="white",
        command=fechar_tudo
    )
    btn_sair.pack(pady=10)

    # Informações do sistema
    info_label = tk.Label(
        root,
        text=f"Usuário: {getpass.getuser()} | Sistema: {platform.system()}",
        font=("Arial", 8),
        fg="gray",
        pady=10
    )
    info_label.pack(side=tk.BOTTOM)

    # Inicia o loop da interface
    root.mainloop()


# ==========================================
# MENU PRINCIPAL (Console)
# ==========================================
def menu_console():
    print("\n" + "="*60)
    print("  SISTEMA DE BACKUP CRIPTOGRAFADO - DSA")
    print("  Projeto 2 - Automação de Processos com Python")
    print("="*60)
    print("1 - Fazer Backup (Caminhos fixos)")
    print("2 - Restaurar Backup (Caminhos fixos)")
    print("3 - Abrir Interface Gráfica")
    print("4 - Sair")
    print("="*60)
    escolha = input("Escolha uma opção: ")
    return escolha


# ==========================================
# MAIN
# ==========================================
if __name__ == "__main__":
    print("\n🔐 Sistema de Backup Criptografado Iniciado")
    print(f"📁 Origem: {CAMINHO_ORIGEM}")
    print(f"📁 Destino: {CAMINHO_DESTINO}")
    print(f"📁 Restauração: {CAMINHO_FINAL}")

    while True:
        opcao = menu_console()

        if opcao == "1":
            fazer_backup_console()
        elif opcao == "2":
            restaurar_backup_console()
        elif opcao == "3":
            print("\n🖥️ Abrindo interface gráfica...")
            interface_grafica()
        elif opcao == "4":
            print("\n👋 Encerrando sistema...")
            break
        else:
            print("\n⚠️ Opção inválida! Tente novamente.")

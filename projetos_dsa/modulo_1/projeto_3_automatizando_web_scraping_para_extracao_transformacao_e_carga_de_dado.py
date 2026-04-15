# Projeto 3 - Automatizando Web Scraping Para Extração, Transformação e Carga de Dados

# Inicie o servidor web com o comando: python -m http.server 8888

# Imports
# pip install openpyxl
import os # Para operações do sistema
import time # Para manipulação de tempo
import sqlite3 # Para banco de dados SQLite
import requests # Para fazer requisições HTTP
import openpyxl # Para manipulação de planilhas Excel
from bs4 import BeautifulSoup # Para parsing de HTML

# Função para limpar o terminal
def dsa_limpa_terminal():
    if os.name == 'nt':  # Para Windows
        os.system('cls')
    else:  # Para Unix/Linux/Mac
        os.system('clear')

# Função para extrair dados da página web
def dsa_extrai_dados(url):
    
    # Faz uma solicitação GET para a URL fornecida
    response = requests.get(url)
    
    # Analisa o conteúdo HTML da resposta
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Encontra todos os blocos de carro na página
    car_blocks = soup.find_all('div', class_='car_block')
    
    # Inicializa uma lista para armazenar os dados extraídos
    dados = []
    
    # Itera sobre cada bloco de carro encontrado
    for block in car_blocks:
        
        # Extrai o nome do carro
        car_name = block.find('span', class_='car_name').text
        
        # Extrai a quantidade de horsepower
        horsepower = block.find('span', class_='horsepower').text
        
        # Extrai o peso e remove vírgulas
        weight_lbs = block.find('span', class_='weight').text.replace(',', '')
        
        # Extrai o tempo de aceleração
        acceleration_sec = block.find('span', class_='acceleration').text

        # Tratar valores ausentes para horsepower
        horsepower = int(horsepower) if horsepower != '-' else None

        # Adiciona os dados extraídos à lista
        dados.append({
            'Car Name': car_name,
            'Horsepower': horsepower,
            'Weight (lbs)': int(weight_lbs),
            'Acceleration (s)': float(acceleration_sec)
        })

    # Retorna a lista de dados extraídos
    return dados

# Função para transformar os dados
def dsa_transforma_dados(dados):
    
    # Loop
    for entrada in dados:
        
        # Converte o peso de libras para quilogramas
        entrada['Weight (kg)'] = entrada['Weight (lbs)'] * 0.453592

    return dados

# Função para salvar os dados em uma planilha Excel
def dsa_salva_dados_excel(dados, nome_arquivo):
    #Criar uma nova planilha Excel
    wb = openpyxl.Workbook()

    # Selecionar a planilha ativa
    ws = wb.active

    # Definir os cabeçalhos das colunas
    ws.title = "Dados DSA"

    # Adicionar os cabeçalhos
    headers = list(dados[0].keys())

    # Adicionar os cabeçalhos na primeira linha da planilha
    ws.append(headers)

    # Adicionar dados
    for entrada in dados:
        ws.append(list(entrada.values()))

    # Salvar a planilha no arquivo especificado
    wb.save(nome_arquivo)

# Função para carregar os dados em um banco de dados SQLite
def dsa_carrega_dados_sqlite(dados, nome_banco):

    # Conectar ao banco de dados SQLite (ou criar se não existir)
    conn = sqlite3.connect(nome_banco)
    cursor = conn.cursor()

    # Criar a tabela se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS car_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_name TEXT,
            horsepower INTEGER,
            weight_kg REAL,
            acceleration_s REAL
        )
    ''')

    # Inserir os dados na tabela
    for entrada in dados:
        cursor.execute('''
            INSERT INTO car_data (car_name, horsepower, weight_kg, acceleration_s)
            VALUES (?, ?, ?, ?)
        ''', (
            entrada['Car Name'],
            entrada['Horsepower'],
            entrada['Weight (kg)'],
            entrada['Acceleration (s)']
        ))

    # Salvar as mudanças e fechar a conexão
    conn.commit()
    conn.close()

# ==========================================
# CONFIGURAÇÃO DE CAMINHOS
# ==========================================
# Diretório onde estão os dados (HTML)
CAMINHO_DADOS = r"C:\Users\User\OneDrive\Documentos\Python\Dev_Python\Abud Python Learning\DSA\Módulo_1-Automação-Excel-e-Engenharia-de-Dados\5_Automacao_de_Processos_e_Engenharia_de_Dados_com_Python_Excel_e_IA"

# Caminhos dos arquivos de saída
caminho_excel = os.path.join(CAMINHO_DADOS, 'dsa_dados.xlsx')
caminho_banco = os.path.join(CAMINHO_DADOS, 'dsa_dados.db')

# URL da página web
url = 'http://localhost:8888/index.html'

# Limpa o terminal
dsa_limpa_terminal()

print("\nExtraindo dados da página web...")
dados = dsa_extrai_dados(url)
time.sleep(2)

#Transformação dos dados
print("\nTransformando os dados...")
dados_transformados = dsa_transforma_dados(dados)
time.sleep(2)

# Salvar os dados em uma planilha Excel
print("\nSalvando os dados em uma planilha Excel...")
dsa_salva_dados_excel(dados_transformados, caminho_excel)
time.sleep(2)

# Carregar os dados no banco de dados
print("\nCarregando os dados no banco de dados...")
dsa_carrega_dados_sqlite(dados_transformados, caminho_banco)
time.sleep(2)

print(f"\n✅ Processo concluído com sucesso!")
print(f"📁 Arquivos salvos em: {CAMINHO_DADOS}\n")




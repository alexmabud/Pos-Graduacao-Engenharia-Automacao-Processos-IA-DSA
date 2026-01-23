# Projeto 3 - Automatizando Web Scraping Para Extração, Transformação e Carga de Dados

# Inicie o servidor web com o comando: python -m http.server 8888

# Imports
# pip install openpyxl
import os
import time
import sqlite3
import requests
import openpyxl
from bs4 import BeautifulSoup

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
        
        # Converter peso de lbs para kg (1 lb = 0.453592 kg)
        entrada['Weight (kg)'] = entrada.pop('Weight (lbs)') * 0.453592
        
        # Converter aceleração de segundos para km/h (1 mph = 1.60934 km/h)
        entrada['Acceleration (km/h)'] = entrada.pop('Acceleration (s)') * 1.60934
    
    return dados

# Função para salvar os dados em uma planilha Excel
def dsa_salva_dados(dados, filename):
    
    # Cria uma nova planilha Excel
    wb = openpyxl.Workbook()
    
    # Seleciona a planilha ativa
    ws = wb.active
    
    # Define o título da planilha ativa
    ws.title = "DadosDSA"

    # Adicionar cabeçalhos
    # Obtém as chaves do primeiro dicionário da lista como cabeçalhos e converte para uma lista
    headers = list(dados[0].keys())
    
    # Adiciona os cabeçalhos à primeira linha da planilha
    ws.append(headers)

    # Adicionar dados
    # Itera sobre cada entrada de dados
    for entrada in dados:
        
        # Adiciona os valores da entrada à planilha
        ws.append(list(entrada.values()))

    # Salva a planilha no arquivo especificado
    wb.save(filename)

# Função para carregar os dados em um banco de dados SQLite
def dsa_carrega_database(dados, db_filename):
    
    # Conecta ao banco de dados SQLite (ou cria um novo arquivo de banco de dados)
    conn = sqlite3.connect(db_filename)
    
    # Cria um cursor para interagir com o banco de dados
    cursor = conn.cursor()
    
    # Cria a tabela 'dsa_carros' se ela não existir, com as colunas especificadas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dsa_carros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_name TEXT,
            horsepower INTEGER,
            weight_kg REAL,
            acceleration_kmh REAL
        )
    ''')
    
    # Itera sobre cada entrada de dados
    for entrada in dados:
        
        # Insere os dados na tabela 'dsa_carros'
        cursor.execute('''
            INSERT INTO dsa_carros (car_name, horsepower, weight_kg, acceleration_kmh)
            VALUES (?, ?, ?, ?)
        ''', (entrada['Car Name'], entrada['Horsepower'], entrada['Weight (kg)'], entrada['Acceleration (km/h)']))
    
    # Confirma as alterações no banco de dados
    conn.commit()
    
    # Fecha a conexão com o banco de dados
    conn.close()

# URL da página web
# Inicie o servidor web com o comando: python -m http.server 8888
url = 'http://localhost:8888/index.html'

# Limpar o terminal
dsa_limpa_terminal()

print("\nProjeto 3 - Automatizando Web Scraping Para Extração, Transformação e Carga de Dados")

# Extração dos dados
print('\nExtraindo os Dados...')
dados = dsa_extrai_dados(url)
time.sleep(2)

# Transformação dos dados
print('\nTransformando os Dados...')
dados_transformados = dsa_transforma_dados(dados)
time.sleep(2)

# Salvando os dados em planilha Excel
print('\nSalvando os Dados em Planilha Excel...')
dsa_salva_dados(dados_transformados, 'dsa_dados.xlsx')
time.sleep(2)

# Carregando os dados no banco de dados
print('\nCarregando os Dados no Banco de Dados...')
dsa_carrega_database(dados_transformados, 'dsa_database.db')
time.sleep(2)

print("\nProcesso Concluído com Sucesso.\n")

# Projeto 4 - Automação de Pipeline Para Extração e Armazenamento de Dados com Selenium
# Versão 1 - Salvando os Dados em Banco de Dados SQLite

# Imports
import re  # Importa a biblioteca 're' para operações de expressões regulares
import time  # Importa a biblioteca 'time' para operações relacionadas ao tempo
import sqlite3  # Importa a biblioteca 'sqlite3' para interagir com bancos de dados SQLite
import pandas as pd  # Importa a biblioteca 'pandas' para manipulação de dados
from selenium import webdriver  # Importa 'webdriver' do Selenium para automação do navegador
from selenium.webdriver.common.by import By  # Importa 'By' para localizar elementos no navegador
from selenium.webdriver.support.ui import WebDriverWait  # Import para espera explícita
from selenium.webdriver.support import expected_conditions as EC  # Import para definir condição de espera
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException  # Importa exceções do Selenium

# Inicializa o navegador Chrome
driver = webdriver.Chrome()

# Define a consulta de busca
query = '15 inch laptop'

# Abre a página da Amazon com a consulta definida
driver.get(f"https://www.amazon.com/s?k={query}")

# Cria um DataFrame vazio para armazenar os dados
laptop_df = pd.DataFrame(columns=['Name', 'Memory', 'Storage', 'Processor'])

# Tenta executar o bloco de código principal
try:

    # Continua a execução até que tenhamos 100 laptops no DataFrame
    while len(laptop_df) < 100:

        # Espera até que todos os elementos estejam visíveis
        WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.XPATH, "//span[@class='a-size-medium a-color-base a-text-normal']"))
        )

        # Encontra todos os elementos que correspondem ao XPATH
        elements = driver.find_elements(By.XPATH, "//span[@class='a-size-medium a-color-base a-text-normal']")
        
        # Itera sobre cada elemento encontrado
        for element in elements:

            # Verifica se o elemento contém '15' ou '15.6' e se o DataFrame tem menos de 100 linhas
            if ('15' in element.text or '15.6' in element.text) and len(laptop_df) < 100:
                
                # Extrai o texto do elemento
                text = element.text
                
                # Usa expressões regulares para encontrar especificações de memória, armazenamento e processador
                # O prefixo r antes das aspas indica uma string "raw" (crua), o que significa que as barras invertidas \ são tratadas literalmente 
                # e não como caracteres de escape. 
                # \d é um metacaractere que representa qualquer dígito numérico de 0 a 9.
                # O sinal de + é o quantificador que significa "um ou mais". Ele faz com que o padrão anterior (\d) corresponda a uma ou mais 
                # ocorrências consecutivas de dígitos.
                memory = re.search(r"\d+GB RAM", text)
                storage = re.search(r"\d+GB SSD|\d+TB SSD|\d+GB HDD|\d+TB HDD", text)

                # [^ \s] significa qualquer caractere que não seja um espaço em branco.
                processor = re.search(r"(i\d|AMD Ryzen \d|Ryzen \d|Intel [^\s]+ \d)", text, re.IGNORECASE)
                
                # Cria um DataFrame temporário para armazenar os dados da linha atual
                temp_df = pd.DataFrame([{
                    'Name': text,
                    'Memory': memory.group(0) if memory else 'N/A',
                    'Storage': storage.group(0) if storage else 'N/A',
                    'Processor': processor.group(0) if processor else 'N/A'
                }])
                
                # Concatena o DataFrame temporário com o DataFrame principal
                laptop_df = pd.concat([laptop_df, temp_df], ignore_index=True)

        # Tenta encontrar e clicar no botão de próxima página
        try:
            next_button = driver.find_element(By.XPATH, "//a[@class='s-pagination-item s-pagination-next s-pagination-button s-pagination-separator']")
            
            # Verifica se já temos 100 laptops no DataFrame
            if len(laptop_df) >= 100:
                break
            
            # Clica no botão de próxima página
            driver.execute_script("arguments[0].click();", next_button)

            # Espera 2 segundos para carregar a próxima página
            time.sleep(2)

        # Se o botão não for encontrado, sai do loop
        except (NoSuchElementException, NoSuchWindowException):
            break

# Sempre executa o bloco de código abaixo, independente de exceções
finally:
    # Fecha o navegador
    driver.quit()

# Salva o DataFrame em um banco de dados SQLite
# Conecta ao banco de dados SQLite (ou cria se não existir)
conn = sqlite3.connect('laptops.db')

# Salva os dados do DataFrame na tabela 'laptops' do banco de dados
laptop_df.to_sql('laptops', conn, if_exists='replace', index=False)

# Fecha a conexão com o banco de dados
conn.close()

# Imprime a quantidade de laptops salvos no banco de dados
print(f"\nOs dados de {len(laptop_df)} laptops de 15 polegadas foram carregados no banco de dados 'laptops.db'.\n")

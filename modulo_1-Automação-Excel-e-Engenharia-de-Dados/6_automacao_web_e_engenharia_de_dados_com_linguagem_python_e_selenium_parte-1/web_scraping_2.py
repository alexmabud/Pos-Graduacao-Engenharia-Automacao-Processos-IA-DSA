# Automação Web e Engenharia de Dados com Linguagem Python e Selenium - Script 2

# Importa o módulo 'webdriver' da biblioteca 'selenium'
from selenium import webdriver

# Importa a classe 'By' do módulo 'webdriver.common.by' da biblioteca 'selenium'
from selenium.webdriver.common.by import By

# Importa a classe 'WebDriverWait' do módulo 'webdriver.support.ui' da biblioteca 'selenium'
from selenium.webdriver.support.ui import WebDriverWait

# Importa a classe 'expected_conditions' como 'EC' do módulo 'webdriver.support' da biblioteca 'selenium'
from selenium.webdriver.support import expected_conditions as EC

# Importa a biblioteca 'csv' para manipulação de arquivos CSV
import csv

# Cria uma nova instância do navegador Chrome
driver = webdriver.Chrome()

# Define a query de busca
query = '15 inch laptop'

# Abre a URL especificada no navegador com a query de busca
driver.get(f"https://www.amazon.com/s?k={query}")

try:

    # Espera até que os contêineres dos produtos estejam visíveis (máximo de 10 segundos)
    elements = WebDriverWait(driver, 10).until(
        EC.visibility_of_all_elements_located((By.XPATH, "//span[@class='a-size-medium a-color-base a-text-normal']"))
    )

    # Coleta os nomes dos laptops que incluem "15" ou "15.6" no título
    laptop_names = [element.text for element in elements if '15' in element.text or '15.6' in element.text]

    # Abre um arquivo CSV para escrita com codificação UTF-8
    with open('laptops_2.csv', 'w', newline='', encoding='utf-8') as file:
        
        # Cria um escritor CSV
        writer = csv.writer(file)
        
        # Escreve o cabeçalho no arquivo CSV
        writer.writerow(['Laptop Name'])
        
        # Escreve os nomes dos laptops no arquivo CSV
        for name in laptop_names:
            writer.writerow([name])

    # Exibe uma mensagem indicando a quantidade de nomes salvos no arquivo
    print(f"Salvando {len(laptop_names)} nomes de laptops no arquivo em disco.")

# Finaliza a execução e fecha o navegador
finally:
    driver.quit()

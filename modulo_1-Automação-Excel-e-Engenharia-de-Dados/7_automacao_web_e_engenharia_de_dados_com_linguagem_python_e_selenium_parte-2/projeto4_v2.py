# Projeto 4 - Automação de Pipeline Para Extração e Armazenamento de Dados com Selenium
# Versão 2 - Salvando os Dados em Planilha Excel

# pip install openpyxl

# Imports
import re  
import time  
import pandas as pd  
from selenium import webdriver  
from selenium.webdriver.common.by import By  
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC  
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException  

# Inicializa o navegador Chrome
driver = webdriver.Chrome()

# Define a consulta de busca
query = '15 inch laptop'

# Abre a página da Amazon com a consulta definida
driver.get(f"https://www.amazon.com/s?k={query}")

# Cria um DataFrame vazio para armazenar os dados
laptop_df = pd.DataFrame(columns=['Name', 'Memory', 'Storage', 'Processor'])

try:
    while len(laptop_df) < 100:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.XPATH, "//span[@class='a-size-medium a-color-base a-text-normal']"))
        )
        elements = driver.find_elements(By.XPATH, "//span[@class='a-size-medium a-color-base a-text-normal']")
        for element in elements:
            if ('15' in element.text or '15.6' in element.text) and len(laptop_df) < 100:
                text = element.text
                memory = re.search(r"\d+GB RAM", text)
                storage = re.search(r"\d+GB SSD|\d+TB SSD|\d+GB HDD|\d+TB HDD", text)
                processor = re.search(r"(i\d|AMD Ryzen \d|Ryzen \d|Intel [^\s]+ \d)", text, re.IGNORECASE)
                
                # Criar um DataFrame temporário para armazenar os dados da linha atual
                temp_df = pd.DataFrame([{
                    'Name': text,
                    'Memory': memory.group(0) if memory else 'N/A',
                    'Storage': storage.group(0) if storage else 'N/A',
                    'Processor': processor.group(0) if processor else 'N/A'
                }])
                
                # Concatenar o DataFrame temporário com o DataFrame principal
                laptop_df = pd.concat([laptop_df, temp_df], ignore_index=True)

        try:
            next_button = driver.find_element(By.XPATH, "//a[@class='s-pagination-item s-pagination-next s-pagination-button s-pagination-separator']")
            if len(laptop_df) >= 100:
                break
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(2)
        except (NoSuchElementException, NoSuchWindowException):
            break

finally:
    driver.quit()

# Salva o DataFrame em um arquivo Excel
laptop_df.to_excel('laptops.xlsx', index=False)

print(f"\nOs dados de {len(laptop_df)} laptops de 15 polegadas foram salvos na planilha 'laptops.xlsx'.\n")

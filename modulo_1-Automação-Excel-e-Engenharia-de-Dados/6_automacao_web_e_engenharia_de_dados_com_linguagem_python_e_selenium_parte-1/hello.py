# Importa o módulo 'webdriver' da biblioteca 'selenium'
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Cria uma nova instância do navegador Chrome com gerenciamento automático do driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

try:
    # Abre a URL especificada no navegador
    driver.get("http://selenium.dev")
    print("✅ Página carregada com sucesso!")
finally:
    # Fecha o navegador
    driver.quit()
    print("✅ Navegador fechado!")

# Importa o módulo 'webdriver' da biblioteca 'selenium'
from selenium import webdriver

# Cria uma nova instância do navegador Chrome
driver = webdriver.Chrome()

# Abre a URL especificada no navegador
driver.get("http://selenium.dev")

# Fecha o navegador
driver.quit()

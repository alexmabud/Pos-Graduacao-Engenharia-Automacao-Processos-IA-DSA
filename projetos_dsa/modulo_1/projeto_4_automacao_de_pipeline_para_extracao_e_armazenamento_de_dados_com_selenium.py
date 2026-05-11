# Projeto 4 - Automação de Pipeline Para Extração e Armazenamento de Dados com Selenium

# Imports
import os  # Importa a biblioteca 'os' para operações com caminhos
import re  # Importa a biblioteca 're' para operações de expressões regulares
import time  # Importa a biblioteca 'time' para operações relacionadas ao tempo
import sqlite3  # Importa a biblioteca 'sqlite3' para interagir com bancos de dados SQLite
import pandas as pd  # Importa a biblioteca 'pandas' para manipulação de dados
from selenium import webdriver  # Importa 'webdriver' do Selenium para automação do navegador
from selenium.webdriver.common.by import By  # Importa 'By' para localizar elementos no navegador
from selenium.webdriver.support.ui import WebDriverWait  # Import para espera explícita
from selenium.webdriver.support import expected_conditions as EC  # Import para definir condição de espera
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException, TimeoutException  # Importa exceções do Selenium
from webdriver_manager.chrome import ChromeDriverManager  # Importa gerenciador automático do ChromeDriver
from selenium.webdriver.chrome.service import Service  # Importa Service para configurar o ChromeDriver
import undetected_chromedriver as uc  # Importa Chrome não detectável

# Define o caminho base onde os dados serão salvos
CAMINHO_BASE = r"C:\Users\User\OneDrive\Documentos\Python\Dev_Python\Abud Python Learning\DSA\Módulo_1-Automação-Excel-e-Engenharia-de-Dados\7_automacao_web_e_engenharia_de_dados_com_linguagem_python_e_selenium_parte-2"

# Define o caminho completo do banco de dados
caminho_banco = os.path.join(CAMINHO_BASE, 'laptops.db')

# Define o caminho completo do arquivo Excel
caminho_excel = os.path.join(CAMINHO_BASE, 'laptops.xlsx')

# Inicializa o navegador Chrome não detectável
try:
    options = uc.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-notifications')
    driver = uc.Chrome(options=options)
except Exception as e:
    print(f"Erro ao inicializar Chrome não detectável: {e}")
    print("Tentando com Chrome padrão...")
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

# Define a consulta de busca
query = 'notebook 15 polegadas'

# Abre a página do Mercado Livre com a consulta definida
print(f"Acessando Mercado Livre para buscar '{query}'...")
driver.get(f"https://lista.mercadolivre.com.br/{query.replace(' ', '-')}")

# Aguarda a página carregar completamente
print("Aguardando o carregamento da página (15 segundos)...")
time.sleep(15)

# Tira um print da página para debug
print(f"Título da página: {driver.title}")
print(f"URL atual: {driver.current_url}")

# Debug: Salva o HTML da página para análise (comentado para performance)
# html_debug_path = os.path.join(CAMINHO_BASE, 'page_source.html')
# with open(html_debug_path, 'w', encoding='utf-8') as f:
#     f.write(driver.page_source)
# print(f"📄 HTML da página salvo em: {html_debug_path}")

# Cria um DataFrame vazio para armazenar os dados
laptop_df = pd.DataFrame(columns=['Name', 'Memory', 'Storage', 'Processor'])

# Tenta executar o bloco de código principal
try:

    # Continua a execução até que tenhamos 100 laptops no DataFrame
    while len(laptop_df) < 100:

        try:
            # Primeiro, espera pelo container principal de produtos
            print("Aguardando containers de produtos...")
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.ui-search-layout__item"))
            )
            print("✅ Containers de produtos encontrados!")

            # Rola a página para baixo para ativar o lazy loading
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
            time.sleep(2)

            # Espera pelos títulos dos produtos usando a classe correta do Mercado Livre
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "poly-component__title"))
            )

            # Encontra todos os títulos de produtos
            elements = driver.find_elements(By.CLASS_NAME, "poly-component__title")
            print(f"✅ Encontrados {len(elements)} produtos na página")

        except TimeoutException:
            print("⚠️ Tempo limite excedido. Não foi possível encontrar produtos.")
            screenshot_path = os.path.join(CAMINHO_BASE, 'debug_screenshot.png')
            driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot salva em: {screenshot_path}")
            break
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            break

        # Itera sobre cada elemento encontrado
        for element in elements:

            # Verifica se o elemento contém '15' ou '15.6' e se o DataFrame tem menos de 100 linhas
            if ('15' in element.text or '15.6' in element.text) and len(laptop_df) < 100:

                # Extrai o texto do elemento
                text = element.text

                # Usa expressões regulares para encontrar especificações de memória, armazenamento e processador
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

        # Tenta encontrar o botão "Próxima" para ir para a próxima página
        try:
            # Verifica se ja há 100 laptops no DataFrame antes de clicar no botão
            if len(laptop_df) >= 100:
                break

            # Tenta múltiplos seletores para o botão de próxima página
            next_button = None
            selectors = [
                "//a[contains(@title, 'Próxim')]",
                "//a[contains(text(), 'Seguinte')]",
                "//a[@class='andes-pagination__link'][@title='Seguinte']",
                "//li[@class='andes-pagination__button--next']/a"
            ]

            for selector in selectors:
                try:
                    next_button = driver.find_element(By.XPATH, selector)
                    if next_button:
                        print(f"✅ Botão 'Próxima' encontrado!")
                        break
                except:
                    continue

            if next_button:
                # Clica no botão "Próxima"
                driver.execute_script("arguments[0].click();", next_button)

                # Espera 3 segundos para carregar a próxima página
                print(f"Coletados {len(laptop_df)} produtos até agora. Indo para próxima página...")
                time.sleep(3)
            else:
                print("Não foi possível encontrar o botão de próxima página.")
                break

        # Se o botão "Próxima" não for encontrado, sai do loop
        except NoSuchElementException:
            print("Não há mais páginas disponíveis.")
            break

# Sempre executa o bloco de código abaixo, independentemente de erros anteriores
finally:
    # Fecha o navegador
    try:
        driver.quit()
    except:
        pass  # Ignora erros durante o fechamento do navegador

# Verifica se há dados para salvar
if len(laptop_df) > 0:
    # Salva os dados em um banco de dados SQLite
    # Conecta ao banco de dados (ou cria um novo se não existir)
    conn = sqlite3.connect(caminho_banco)

    # Salva os dados do DataFrame na tabela 'laptops' do banco de dados
    laptop_df.to_sql('laptops', conn, if_exists='replace', index=False)

    # Fecha a conexão com o banco de dados
    conn.close()

    # Salva os dados em um arquivo Excel
    laptop_df.to_excel(caminho_excel, index=False, sheet_name='Laptops')
else:
    print("\n⚠️ AVISO: Nenhum dado foi coletado. Verifique se o site está acessível.")

# Imprime a quantidade de laptops salvos
if len(laptop_df) > 0:
    print(f"\n{'='*60}")
    print(f"✅ Os dados de {len(laptop_df)} notebooks foram carregados com sucesso!")
    print(f"{'='*60}")
    print(f"📊 Banco de Dados SQLite: {caminho_banco}")
    print(f"📊 Arquivo Excel: {caminho_excel}")
    print(f"{'='*60}\n")
else:
    print(f"\n{'='*60}")
    print(f"❌ ERRO: Nenhum dado foi coletado!")
    print(f"{'='*60}\n")

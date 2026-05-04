# Estudo de Caso - Deploy de Time de Agentes de IA com DeepSeek Para Análise de Inteligência de Mercado

# Imports
import os
import socket
from dotenv import load_dotenv
from phi.agent import Agent  
from phi.model.groq import Groq  
from phi.tools.duckduckgo import DuckDuckGo  
from phi.tools.yfinance import YFinanceTools  

# Verificação antes de carregar variáveis de ambiente
if os.path.exists('.env'):
    load_dotenv()
    print("[DSA-INFO] Variáveis de ambiente carregadas.")
else:
    print("[DSA-ALERTA] Arquivo .env não encontrado. Algumas configurações podem estar ausentes.")

# Função para verificar conexão com a internet
def dsa_verificar_conexao():
    try:
        socket.create_connection(("www.google.com", 80), timeout=5)
        print("[DSA-INFO] Conexão com a internet verificada.")
        return True
    except OSError:
        print("[DSA-ERRO] Sem conexão com a internet! Algumas ferramentas podem não funcionar.")
        return False

# Executa a função
conexao_estabelecida = dsa_verificar_conexao()

# Criando Agentes de IA
print("[DSA-INFO] Inicializando agentes...")

# Define o Agente Financeiro
dsa_agente_financeiro = Agent(name="Analista Financeiro",  
                              model=Groq(id="deepseek-r1-distill-llama-70b"),
                              tools=[YFinanceTools(stock_price=True,  
                                                   analyst_recommendations=True,  
                                                   stock_fundamentals=True)] if conexao_estabelecida else [],  # Evita erro se não houver conexão
                              show_tool_calls=True,  
                              markdown=True,  
                              instructions=["Crie tabelas para comparações", 
                                            "Gere os resultados com o idioma Português do Brasil"])

# Define o Agente de Pesquisa
dsa_agente_pesquisa = Agent(name="Pesquisador Web",  
                            model=Groq(id="deepseek-r1-distill-llama-70b"),
                            tools=[DuckDuckGo()] if conexao_estabelecida else [],  # Evita erro se não houver conexão
                            show_tool_calls=True,  
                            markdown=True,  
                            instructions=["Inclua sempre as fontes das informações que você coleta", 
                                          "Gere os resultados com o idioma Português do Brasil",
                                          "Use fontes confiáveis, você é um Analista de Pesquisa Sênior"])

# Define o Time de Agentes
dsa_time_agentes = Agent(team=[dsa_agente_financeiro, dsa_agente_pesquisa], 
                         model=Groq(id="deepseek-r1-distill-llama-70b"),
                         show_tool_calls=True,  
                         markdown=True,  
                         instructions=["Inclua sempre a fonte das informações coletadas", 
                                       "Crie tabelas para comparações",
                                       "Gere os resultados com o idioma Português do Brasil"],
                         debug_mode=True)

print("[DSA-INFO] Agentes prontos para análise.")

# Executando a análise
print("[DSA-INFO] Obtendo recomendações e informações sobre a Apple...")

# Executa o time de agentes
dsa_time_agentes.print_response("Resumir as recomendações dos analistas sobre investimentos e compartilhar as informações mais recentes sobre a Apple.")





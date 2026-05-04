# Projeto 1 - Reasoning, RAG e Multi-Agente Setup (ReAct Agents)

# Imports
import os
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.knowledge.pdf import PDFUrlKnowledgeBase
from phi.vectordb.lancedb import LanceDb, SearchType
from phi.embedder.openai import OpenAIEmbedder
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.yfinance import YFinanceTools
from phi.cli.console import console
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
try:
    load_dotenv()
except Exception as e:
    print(f"Erro ao carregar variáveis de ambiente: {e}")

# Caminho para o banco de dados do RAG
db_uri = "rag/lancedb"

try:

    # Cria o banco de dados vetorial a partir de um arquivo PDF com relatório anual da Nvidia
    banco_vetorial = PDFUrlKnowledgeBase(
        urls = ["https://s201.q4cdn.com/141608511/files/doc_financials/2024/ar/NVIDIA-2024-Annual-Report.pdf"],
        vector_db = LanceDb(table_name = "dsavectordb", 
                            uri = db_uri, 
                            search_type = SearchType.vector, 
                            embedder = OpenAIEmbedder(model = "text-embedding-3-small"))
    )
    
    # Carrega o banco de dados (pode comentar esta linha para a segunda execução em diante)
    # Upsert faz update ou insert dependendo se o documento já estiver ou não no banco vetorial
    banco_vetorial.load(upsert=True)
except Exception as e:
    print(f"Erro ao criar ou carregar o banco vetorial: {e}")

try:
    # Cria o Agente 1
    agente_pesquisa_dsa = Agent(
        name = "Agente de Pesquisa",
        role = "Pesquisar na Web",
        model = OpenAIChat(id = "gpt-4o"),
        tools = [DuckDuckGo()],
        instructions = ["Gere a resposta no idioma Português do Brasil"],
        markdown = True,
        show_tool_calls = True
    )
    
    # Cria o Agente 2
    agente_financeiro_dsa = Agent(
        name = "Agente Financeiro",
        role = "Coletar Dados de Ativos Financeiros",
        model = OpenAIChat(id="gpt-4o"),
        tools = [YFinanceTools(stock_price = True, 
                               analyst_recommendations = True, 
                               company_info = True, 
                               company_news = True)],
        instructions = ["Sempre use tabelas para exibir dados", "Gere a resposta no idioma Português do Brasil"],
        markdown = True,
        show_tool_calls = True
    )
except Exception as e:
    print(f"Erro ao criar os agentes: {e}")

try:
    # Cria o Time de Agentes (Multi-Agent)
    multi_agente_com_raciocinio_rag = Agent(
        team = [agente_pesquisa_dsa, agente_financeiro_dsa],
        knowledge = banco_vetorial,
        show_tool_calls = True,
        reasoning = True,
        markdown = True,
        structured_outputs = True
    )
except Exception as e:
    print(f"Erro ao criar o time de agentes: {e}")

# Define uma tarefa para o Time de Agentes
tarefa = "Existe relacao entre os elementos juridicos e os dados financeiros da Nvidia? Verifique o relatorio financeiro no banco de dados e gere a resposta em Portugues do Brasil"

try:
    # Define o formato para imprimir as regras no console (terminal ou prompt de comando)
    console.rule("[bold yellow]RAG Reasoning Agent[/bold yellow]")
    
    # Imprime o resultado
    multi_agente_com_raciocinio_rag.print_response(tarefa, 
                                                   stream = True, 
                                                   show_full_reasoning = True)
except Exception as e:
    print(f"Erro ao processar a tarefa: {e}")




# Projeto 1 - Reasoning, RAG e Multi-Agente Setup (ReAct Agents)

# Imports
import os
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.yfinance import YFinanceTools
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

try:

    # Criação do Agente Financeiro com ferramentas para consulta de dados financeiros
    agente_financeiro_dsa = Agent(
        name = "Agente Financeiro",
        role = "Coletar Dados de Ativos Financeiros",
        model = OpenAIChat(id = "gpt-4o"),
        tools = [
            YFinanceTools(
                stock_price = True, 
                analyst_recommendations = True, 
                company_info = True, 
                company_news = True
            )
        ],
        instructions = ["Sempre use tabelas para exibir dados", "Gere a resposta no idioma Português do Brasil"],
        markdown = True,
        show_tool_calls = True
    )

    # Solicita ao agente recomendações de analistas para a ação NVDA (Nvidia)
    agente_financeiro_dsa.print_response("Compartilhe recomendações de analistas para NVDA.", stream = True)

except Exception as e:
    # Captura e exibe erros que possam ocorrer durante a execução
    print(f"Ocorreu um erro: {e}")

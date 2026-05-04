# Projeto 1 - Reasoning, RAG e Multi-Agente Setup (ReAct Agents)

# Imports
import os
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.cli.console import console
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.yfinance import YFinanceTools
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

try:
    # Criação do Agente Jurídico para pesquisas na web
    agente_pesquisa_dsa = Agent(
        name = "Agente de Pesquisa",
        role = "Pesquisar na Web",
        model = OpenAIChat(id = "gpt-4o"),
        tools = [DuckDuckGo()],
        instructions = ["Gere a resposta no idioma Português do Brasil"],
        markdown = True,
        show_tool_calls = True
    )

    # Criação do Agente Financeiro para coleta de dados financeiros
    agente_financeiro_dsa = Agent(
        name = "Agente Financeiro",
        role = "Coletar Dados de Ativos Financeiros",
        model = OpenAIChat(id="gpt-4o"),
        tools = [YFinanceTools(
            stock_price = True,
            analyst_recommendations = True,
            company_info = True,
            company_news = True
        )],
        instructions = ["Sempre use tabelas para exibir dados", "Gere a resposta no idioma Português do Brasil"],
        markdown = True,
        show_tool_calls = True
    )

    # Criação do time de agentes (Multi-Agent)
    multi_agente_com_raciocinio = Agent(
        team = [agente_pesquisa_dsa, agente_financeiro_dsa],
        show_tool_calls = True,
        reasoning = True,
        markdown = True,
        structured_outputs = True
    )

    # Define uma tarefa para o Time de Agentes
    tarefa = "Existe relacao entre os elementos juridicos e os dados financeiros da Nvidia?"

    # Define o formato para imprimir as regras no console (terminal ou prompt de comando)
    console.rule("[bold yellow]Reasoning Agent[/bold yellow]")

    # Executa a tarefa e imprime o resultado
    try:
        multi_agente_com_raciocinio.print_response(
            tarefa,
            stream = True,
            show_full_reasoning = True
        )
    except Exception as e:
        print(f"Erro ao executar a tarefa: {e}")

except Exception as e:
    print(f"Erro ao inicializar os agentes: {e}")



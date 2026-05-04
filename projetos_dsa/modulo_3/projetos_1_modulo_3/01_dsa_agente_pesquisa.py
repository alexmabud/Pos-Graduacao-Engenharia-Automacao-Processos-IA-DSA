# Projeto 1 - Reasoning, RAG e Multi-Agente Setup (ReAct Agents)

# Imports
import os
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo
from dotenv import load_dotenv

# Bloco de execução
try:

    # Carrega variáveis de ambiente do arquivo .env
    load_dotenv()

    # Criação do Agente com tratamento de erro
    try:
        agente_pesquisa_dsa = Agent(name = "Agente de Pesquisa",
                                    role = "Pesquisar na Web",
                                    model = OpenAIChat(id = "gpt-4o"),
                                    tools = [DuckDuckGo()],
                                    instructions = ["Gere a resposta no idioma Português do Brasil"],
                                    markdown = True,
                                    show_tool_calls = True)
    except Exception as e:
        print(f"Erro ao criar o agente: {e}")
        agente_pesquisa_dsa = None

    # Verifica se o agente foi criado com sucesso antes de executar a consulta
    if agente_pesquisa_dsa:
        try:
            agente_pesquisa_dsa.print_response("Quais os fatos jurídicos recentes ligados à Nvidia?", stream = True)
        except Exception as e:
            print(f"Erro ao obter resposta do agente: {e}")
    else:
        print("O agente não foi criado corretamente. Verifique os erros anteriores.")

except Exception as e:
    print(f"Erro inesperado: {e}")

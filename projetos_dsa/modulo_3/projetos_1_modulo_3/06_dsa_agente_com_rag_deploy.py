# Projeto 1 - Reasoning, RAG e Multi-Agente Setup (ReAct Agents)

# Imports
import os
import streamlit as st
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
load_dotenv()

# Configuração da página do Streamlit
st.set_page_config(page_title = "Data Science Academy", page_icon = ":100:", layout = "centered")

st.title(":100: Data Science Academy")
st.title("🔍 Reasoning RAG Multi-Agent")

# Criando banco vetorial
db_uri = "rag/lancedb"

# Carregar o banco vetorial existente sem reprocessar o PDF
banco_vetorial = PDFUrlKnowledgeBase(
    urls = [],  # Lista vazia para não baixar PDFs novamente
    vector_db = LanceDb(table_name = "dsavectordb",
                        uri = db_uri,
                        search_type = SearchType.vector,
                        embedder = OpenAIEmbedder(model = "text-embedding-3-small")  # Modelo usado na indexação
    )
)

# Criando agentes
agente_pesquisa_dsa = Agent(
    name = "Agente de Pesquisa",
    role = "Pesquisar na Web",
    model = OpenAIChat(id = "gpt-4o"),
    tools = [DuckDuckGo()],
    instructions = ["Gere a resposta no idioma Português do Brasil"],
    markdown = True,
    show_tool_calls = False
)

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
    show_tool_calls = False
)

multi_agente_com_raciocinio_rag = Agent(
    team = [agente_pesquisa_dsa, agente_financeiro_dsa],
    knowledge = banco_vetorial,
    show_tool_calls = True,
    reasoning = True,
    markdown = True,
    structured_outputs = True
)

# Input do usuário
tarefa = st.text_area("📝 Insira Sua Pergunta Para os Agentes de IA:", 
                      "Existe relação entre os elementos jurídicos e os dados financeiros da Nvidia?")

if st.button("Executar Análise"):
    with st.spinner("⏳ Os Agentes de IA Estão Processando Sua Consulta. Aguarde..."):
        try:
            response = multi_agente_com_raciocinio_rag.run(tarefa)
            
            # Debug: Verificar estrutura da resposta
            #st.write("Debug - Tipo da resposta:", type(response))
            #st.write("Debug - Conteúdo bruto da resposta:", response)

            # Extraindo somente o conteúdo relevante
            if hasattr(response, "get_content_as_string"):
                resposta_formatada = response.get_content_as_string() 
            elif hasattr(response, "content") and response.content is not None:
                resposta_formatada = response.content 
            else:
                resposta_formatada = "Erro: Resposta não contém conteúdo válido."

            st.markdown("### 📌 Resposta dos Agentes:")
            st.write(resposta_formatada)

        except Exception as e:
            st.error(f"Erro ao processar a tarefa: {e}")





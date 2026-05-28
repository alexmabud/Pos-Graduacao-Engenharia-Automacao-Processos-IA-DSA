# Projeto 8 - Agentes de IA Para Deep Research com OpenAI Agents SDK e Firecrawl

# Importa o módulo asyncio para permitir execução assíncrona de funções
import asyncio

# Importa o Streamlit para construir a interface web interativa
import streamlit as st

# Importa o módulo os para acesso a variáveis de ambiente e operações de sistema
import os

# Carrega variáveis de ambiente a partir de um arquivo .env
from dotenv import load_dotenv

# Importa tipos genéricos do typing para anotações de funções
from typing import Dict, Any, List

# Importa classes principais do SDK de agentes da OpenAI
from agents import Agent, Runner, trace

# Define a função para configurar a chave padrão da OpenAI
from agents import set_default_openai_key

# Importa a aplicação Firecrawl para pesquisa em profundidade
from firecrawl import FirecrawlApp

# Importa decorator para registrar ferramentas usadas pelos agentes
from agents.tool import function_tool

# Executa o carregamento das variáveis definidas no arquivo .env
load_dotenv()

# Configura parâmetros iniciais da página Streamlit, como título, ícone e layout
st.set_page_config(page_title="Data Science Academy", page_icon=":100:", layout="wide")

# Se a chave da OpenAI não estiver no estado da sessão, inicializa com valor do ambiente
if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = os.getenv("OPENAI_API_KEY", "")

# Se a chave do Firecrawl não estiver no estado da sessão, inicializa com valor do ambiente
if "firecrawl_api_key" not in st.session_state:
    st.session_state.firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY", "")

# Abre a barra lateral para configurações de API
with st.sidebar:

    # Exibe título da seção de configuração das APIs
    st.title("Configuração das APIs")
    
    # Campo para entrada da chave da OpenAI, ocultando caracteres digitados
    openai_api_key = st.text_input(
        "OpenAI API Key", 
        value=st.session_state.openai_api_key,
        type="password"
    )
    
    # Campo para entrada da chave do Firecrawl, ocultando caracteres digitados
    firecrawl_api_key = st.text_input(
        "Firecrawl API Key", 
        value=st.session_state.firecrawl_api_key,
        type="password"
    )
    
    # Atualiza o estado da sessão e define a chave padrão se o usuário inserir valor
    if openai_api_key:
        st.session_state.openai_api_key = openai_api_key
        set_default_openai_key(openai_api_key)
    
    # Atualiza o estado da sessão com a chave do Firecrawl quando fornecida
    if firecrawl_api_key:
        st.session_state.firecrawl_api_key = firecrawl_api_key

# Define o título e descrição do projeto na interface
st.title("📘 Agentes de IA Para Deep Research com OpenAI Agents SDK e Firecrawl")
st.markdown("Projeto 8 do Curso Construção e Deploy de Agentes de IA")

# Campo de texto para o usuário informar o tópico de pesquisa
research_topic = st.text_input("Digite o Tópico Para Pesquisa:", placeholder = "Por exemplo: O que é áudio Hi-Fi e quais dispositivos usar?")

# Define a ferramenta assíncrona de deep research usando o decorator function_tool
@function_tool
async def deep_research(query: str, max_depth: int, time_limit: int, max_urls: int) -> Dict[str, Any]:
    
    # Bloco para capturar possíveis exceções durante a pesquisa
    try:

        # Instancia o cliente Firecrawl com a chave de API armazenada na sessão
        firecrawl_app = FirecrawlApp(api_key = st.session_state.firecrawl_api_key)
        
        # Parâmetros para a pesquisa profunda
        params = {
            "maxDepth": max_depth,
            "timeLimit": time_limit,
            "maxUrls": max_urls
        }
        
        # Função de callback para exibir atividades de progresso na interface
        def on_activity(activity):
            st.write(f"[{activity['type']}] {activity['message']}")
        
        # Exibe um indicador de carregamento enquanto a pesquisa é realizada
        with st.spinner("Executando a deep research..."):
            results = firecrawl_app.deep_research(
                query = query,
                params = params,
                on_activity = on_activity
            )
        
        # Retorna resultados estruturados com análise final e fontes encontradas
        return {
            "success": True,
            "final_analysis": results['data']['finalAnalysis'],
            "sources_count": len(results['data']['sources']),
            "sources": results['data']['sources']
        }

    # Trata erros e exibe mensagem de falha para o usuário
    except Exception as e:
        st.error(f"Deep research error: {str(e)}")
        return {"error": str(e), "success": False}

# Configuração do agente responsável pela pesquisa inicial
dsa_research_agent = Agent(
    name = "dsa_research_agent",
    instructions = """Você é um assistente de pesquisa que pode realizar pesquisas na web sobre qualquer tópico.

    Quando for apresentado um tópico ou questão de pesquisa:
    1. Use a ferramenta deep_research para reunir informações abrangentes
       - Use sempre estes parâmetros:
         * max_depth: 3 (para profundidade moderada)
         * time_limit: 180 (3 minutos)
         * max_urls: 5 (fontes suficientes)
    2. A ferramenta pesquisará na web, analisará várias fontes e fornecerá uma síntese
    3. Revise os resultados da pesquisa e organize-os em um relatório bem estruturado
    4. Incluir citações adequadas para todas as fontes
    5. Destacar as principais descobertas e percepções
    """,
    tools = [deep_research]
)

# Configuração do agente responsável pelo aprimoramento do relatório
dsa_elaboration_agent = Agent(
    name="dsa_elaboration_agent",
    instructions="""Você é um especialista em aprimoramento de conteúdo, especializado em elaboração de pesquisas.

    Quando for apresentado um relatório de pesquisa:
    1. Analisar a estrutura e o conteúdo do relatório
    2. Melhorar o relatório por meio de:
       - Adicionar explicações mais detalhadas de conceitos complexos
       - Incluir exemplos relevantes, estudos de caso e aplicações do mundo real
       - Expandir os pontos principais com contexto e nuances adicionais
       - Adicionar descrições de elementos visuais (gráficos, diagramas, infográficos)
       - Incorporar as últimas tendências e previsões futuras
       - Sugerir implicações práticas para diferentes partes interessadas
    3. Manter o rigor acadêmico e a precisão dos fatos
    4. Preservar a estrutura original, tornando-a mais abrangente
    5. Garantir que todas as adições sejam relevantes e valiosas para o tópico
    """
)

# Função principal que orquestra o fluxo de pesquisa e elaboração
async def run_research_process(topic: str):
    
    # Indicador de carregamento para a pesquisa inicial
    with st.spinner("Conduzindo a pesquisa inicial..."):
        research_result = await Runner.run(dsa_research_agent, topic)
        initial_report = research_result.final_output
    
    # Expansível para exibir o relatório inicial ao usuário
    with st.expander("Visualizar o Relatório da Pesquisa"):
        st.markdown(initial_report)
    
    # Indicador de carregamento durante a fase de aprimoramento do relatório
    with st.spinner("Melhorando o relatório com informações adicionais..."):
        
        elaboration_input = f"""
        TÓPICO DE PESQUISA: {topic}
        
        RELATÓRIO DE PESQUISA INICIAL:
        {initial_report}
        
        Complemente este relatório de pesquisa com informações adicionais, exemplos, estudos de caso
        e insights mais aprofundados, mantendo seu rigor acadêmico e precisão factual.
        """
        
        elaboration_result = await Runner.run(dsa_elaboration_agent, elaboration_input)
        enhanced_report = elaboration_result.final_output
    
    return enhanced_report

# Botão que inicia o processo de pesquisa quando clicado, validando chaves e tópico
if st.button("Iniciar Pesquisa", disabled = not (openai_api_key and firecrawl_api_key and research_topic)):
    
    if not openai_api_key or not firecrawl_api_key:
        st.warning("Por favor, insira ambas as chaves de API na barra lateral.")
    elif not research_topic:
        st.warning("Por favor, insira um tópico de pesquisa.")
    else:
        try:
            # Placeholder para atualizar conteúdo de relatório dinamicamente
            report_placeholder = st.empty()
            
            # Executa o fluxo de pesquisa de forma síncrona ao Streamlit
            enhanced_report = asyncio.run(run_research_process(research_topic))
            
            # Exibe o relatório aprimorado e disponibiliza botão de download
            report_placeholder.markdown("## Relatório de Pesquisa Aprimorado")
            report_placeholder.markdown(enhanced_report)
            
            st.download_button(
                "Download do Relatório",
                enhanced_report,
                file_name=f"{research_topic.replace(' ', '_')}_report.md",
                mime="text/markdown"
            )
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Separa visualmente conteúdo principal de instruções adicionais
st.markdown("---")

# Exibe nota de rodapé com créditos do projeto
st.markdown("Produzido com OpenAI Agents SDK e Firecrawl na Data Science Academy") 

# Insere divisor e título na barra lateral para instruções ao usuário
st.sidebar.divider()
st.sidebar.title("Instruções")

# Mensagem explicativa sobre limitações e boas práticas ao usar a ferramenta
st.sidebar.markdown("""
Digite o tópico desejado para pesquisa na caixa ao lado.

**A versão gratuita do Firecrawl tem limitações.**

IA Generativa comete erros. **SEMPRE** use seu conhecimento para verificar as respostas.
""")

# Botão de suporte na barra lateral que exibe contato para dúvidas
if st.sidebar.button("Suporte"):
    st.sidebar.write("Dúvidas? Envie um e-mail para: suporte@datascienceacademy.com.br")









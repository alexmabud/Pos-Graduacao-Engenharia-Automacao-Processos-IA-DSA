# Projeto 7 - Sistema Web de Suporte Técnico Automatizado com Agentic RAG e LLM Routing
# Módulo de App com Agentic RAG e Roteamento

# Importa o módulo os para operações de sistema como verificar arquivos e diretórios
import os

# Importa Streamlit para criar a interface web interativa
import streamlit as st

# Importa função para carregar variáveis de ambiente de um arquivo .env
from dotenv import load_dotenv

# Importa TypedDict e Literal para tipagem do estado do grafo
from typing import TypedDict, Literal

# Importa classes de mensagem base e mensagem humana para LLM routing
from langchain_core.messages import BaseMessage, HumanMessage

# Importa cliente Groq para chamadas ao LLM Groq
from langchain_groq import ChatGroq

# Importa FAISS para buscar documentos via RAG
from langchain_community.vectorstores import FAISS

# Importa modelo de embeddings FastEmbed para transformar textos em vetores
from langchain_community.embeddings import FastEmbedEmbeddings

# Importa ferramenta de busca DuckDuckGo 
from langchain_community.tools import DuckDuckGoSearchRun

# Importa estrutura de grafo de estados e constante de fim
from langgraph.graph import StateGraph, END

# Carrega variáveis de ambiente definidas em .env
load_dotenv()

# Chave API Groq
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    st.error("GROQ_API_KEY não definida no ambiente ou .env!")
    st.stop() 

# Caminho RAG 
VECTORSTORE_PATH = "dsa_faiss_index"

# Cache para o LLM (recurso pesado)
@st.cache_resource
def dsa_carrega_llm_resposta_final():
    
    print("Carregando LLM Groq...") 
    
    try:
        llm = ChatGroq(api_key = groq_api_key, model = "llama-3.3-70b-versatile", temperature = 0.1)
        return llm
    except Exception as e:
        st.error(f"Erro ao carregar LLM: {e}")
        st.stop()

# Cache para o Retriever RAG (recurso pesado)
@st.cache_resource
def dsa_carrega_retriever():
    
    print("Carregando Retriever RAG...") 
    
    if not os.path.exists(VECTORSTORE_PATH):
        st.error(f"Índice FAISS não encontrado em '{VECTORSTORE_PATH}'. Execute 'dsa_p7_setup_rag.py'.")
        st.stop()
    
    try:
        embedding_model = FastEmbedEmbeddings(model_name = "BAAI/bge-small-en-v1.5")
        vector_store = FAISS.load_local(VECTORSTORE_PATH, embedding_model, allow_dangerous_deserialization = True)
        retriever = vector_store.as_retriever(search_kwargs = {'k': 5})
        return retriever
    except Exception as e:
        st.error(f"Erro ao carregar Retriever RAG: {e}")
        st.stop()

# Define a classe de estado do grafo (Agente de IA)
class GraphState(TypedDict):
    query: str
    source_decision: Literal["RAG", "WEB", ""]
    rag_context: str | None
    web_results: str | None
    final_answer: str | None

# Função para o nó de roteamento
def dsa_route_query_node(state: GraphState) -> dict:
    
    """
    Analisa a consulta e decide a fonte de dados (RAG ou WEB).
    Atualiza 'source_decision' no estado.
    """
    
    print("--- Nó: Roteamento da Consulta ---")
    
    query = state["query"]

    # **PROMPT REFINADO COM EXEMPLOS (FEW-SHOT)**
    prompt = f"""Sua tarefa é classificar a consulta de um usuário para direcioná-la à melhor fonte de informação. As fontes são:
    1.  **RAG**: Base de conhecimento interna com documentos de suporte técnico, procedimentos específicos, configurações do nosso sistema, guias internos. Use RAG para perguntas sobre 'como fazer X em nosso sistema', 'qual a configuração de Y', 'documentação interna sobre Z'.
    2.  **WEB**: Busca geral na internet para informações sobre software de terceiros (ex: Anaconda, Python, Excel), notícias de tecnologia, erros genéricos não documentados internamente, informações muito recentes, ou qualquer coisa que não seja específica dos nossos documentos internos.

    Exemplos:
    - Consulta: "Como configuro o servidor de email interno?" -> Resposta: RAG
    - Consulta: "Qual a versão mais recente do Streamlit?" -> Resposta: WEB
    - Consulta: "Qual o procedimento para resetar a senha do sistema ABC?" -> Resposta: RAG
    - Consulta: "Como instalo o interpretador Python no Windows 11" -> Resposta: WEB
    - Consulta: "como instalar o Anaconda Python" -> Resposta: WEB

    Agora, classifique a seguinte consulta:
    Consulta do Usuário: '{query}'

    Com base na consulta, qual é a fonte mais apropriada? Responda APENAS com a palavra 'RAG' ou a palavra 'WEB'."""

    try:
        # **CRIA LLM DEDICADO PARA ROTEAMENTO COM TEMPERATURA MAIS ALTA**
        # Aqui podemos usar um modelo mais simples, como um SLM
        router_llm = ChatGroq(api_key = groq_api_key,
                              model = "llama-3.1-8b-instant",
                              temperature = 0.4)

        # Executa o roteador
        response = router_llm.invoke(prompt)

        # Extrai a resposta
        raw_decision = response.content 

        # DEBUG PRINT ESSENCIAL (Verificar no console!)
        print(f"DEBUG: Decisão do LLM (Roteador de Requisições): '{raw_decision}'")

        # Limpeza do texto de resposta para manter somente a palavra que nos interessa
        decision = raw_decision.strip().upper().replace("'", "").replace('"', '') 

        # Lógica de decisão final (se não for RAG, assume WEB)
        if decision == "RAG":
            final_decision = "RAG"
        else:
            # Se não for RAG, e também não for WEB, loga o valor mas vai para WEB
            if decision != "WEB":
                 print(f"  Decisão inválida/inesperada do roteador: '{raw_decision}'. Usando WEB como fallback.") 
            final_decision = "WEB"

        print(f"  Decisão Final do Roteador: {final_decision}") 

        return {"source_decision": final_decision}

    except Exception as e:
        print(f"  Erro no nó de roteamento: {e}") 
        print("  Usando WEB como fallback devido a erro.") 
        return {"source_decision": "WEB"}

# Função para o nó de retrieve do RAG
def dsa_retrieve_rag_node(state: GraphState) -> dict:
    
    query = state["query"]
    
    try:
        local_retriever = dsa_carrega_retriever() 
        results = local_retriever.invoke(query)
        context = "\n\n".join([doc.page_content for doc in results])
        if not context:
            print("  Nenhum contexto RAG encontrado.") 
            return {"rag_context": "Não foram encontrados documentos internos relevantes."}
        else:
            print(f"  Contexto RAG encontrado ({len(context)} chars).") 
            return {"rag_context": context}
    except Exception as e:
        print(f"  Erro no nó RAG: {e}") 
        return {"rag_context": f"Erro ao buscar nos documentos internos: {e}"}

# Função para o nó de busca na web
def dsa_search_web_node(state: GraphState) -> dict:
    
    query = state["query"]
    
    try:
        web_search_tool = DuckDuckGoSearchRun()
        results = web_search_tool.run(query)
        if not results:
            print("  Nenhum resultado da busca web.") 
            return {"web_results": "Não foram encontrados resultados relevantes na web."}
        else:
            print(f"  Resultados da busca web encontrados ({len(results)} chars).") 
            return {"web_results": results}
    except Exception as e:
        print(f"  Erro no nó Web Search: {e}") 
        return {"web_results": f"Erro ao realizar busca na web: {e}"}

# Função para gerar a resposta final para o usuário
def dsa_generate_answer_node(state: GraphState) -> dict:
    
    print("--- Nó: Geração da Resposta ---") 
    
    query = state["query"]
    rag_context = state.get("rag_context")
    web_results = state.get("web_results")
    context_provided = ""
    source_used = "Nenhuma"

    if rag_context != "Não foram encontrados documentos internos relevantes.":
        context_provided = f"Contexto dos documentos internos:\n{rag_context}"
        source_used = "RAG"
        print("  Usando contexto RAG para gerar resposta.") 
    elif web_results != "Não foram encontrados resultados relevantes na web.":
        context_provided = f"Resultados da busca na web:\n{web_results}"
        source_used = "WEB"
        print("  Usando resultados da web para gerar resposta.") 
    else:
        context_provided = "Nenhuma informação adicional encontrada nas fontes disponíveis."
        print("  Nenhum contexto útil encontrado para gerar resposta.") 

    prompt = f"""Você é um assistente de suporte técnico. Responda à pergunta do usuário de forma clara e concisa, utilizando APENAS as informações fornecidas no contexto abaixo, se houver.
    Consulta do Usuário: {query}
    {context_provided}
    Resposta:"""

    try:
        llm_resposta_final = dsa_carrega_llm_resposta_final()
        response = llm_resposta_final.invoke(prompt)
        final_answer = response.content
        print(f"  Resposta gerada usando fonte: {source_used}") 
        return {"final_answer": final_answer}
    except Exception as e:
        print(f"  Erro no nó de geração: {e}") 
        return {"final_answer": f"Desculpe, ocorreu un erro ao gerar a resposta: {e}"}

# Função para nó de decisão da fonte (RAG ou WEB)
def dsa_decide_source_edge(state: GraphState) -> Literal["retrieve_rag_node", "search_web_node"]:
    
    decision = state["source_decision"]
    
    print(f"--- Aresta Condicional: Decisão recebida = '{decision}' ---") 
    
    if decision == "RAG":
        print("  Aresta: Indo para RAG.") 
        return "retrieve_rag_node"
    else:
        print("  Aresta: Indo para WEB.") 
        return "search_web_node"

# Função para compilar (criar) o grafo do LangGraph (ou seja, o Agente de IA)
@st.cache_resource
def dsa_compile_graph():
    
    print("Compilando o grafo LangGraph...") 
    
    # Cria os nós
    graph_builder = StateGraph(GraphState)
    graph_builder.add_node("route_query_node", dsa_route_query_node)
    graph_builder.add_node("retrieve_rag_node", dsa_retrieve_rag_node)
    graph_builder.add_node("search_web_node", dsa_search_web_node)
    graph_builder.add_node("generate_answer_node", dsa_generate_answer_node)
    graph_builder.set_entry_point("route_query_node")
    
    # Cria a condição para o roteamento
    graph_builder.add_conditional_edges("route_query_node", dsa_decide_source_edge, {
        "retrieve_rag_node": "retrieve_rag_node",
        "search_web_node": "search_web_node",
    })
    
    # Adiciona as arestas
    graph_builder.add_edge("retrieve_rag_node", "generate_answer_node")
    graph_builder.add_edge("search_web_node", "generate_answer_node")
    graph_builder.add_edge("generate_answer_node", END)
    
    # Compila o grafo
    try:
        app = graph_builder.compile()
        print("Grafo compilado com sucesso!") 
        return app
    except Exception as e:
        st.error(f"Erro ao compilar o grafo: {e}")
        st.stop()

# Configurar página do Streamlit
st.set_page_config(page_title="Data Science Academy", page_icon=":100:", layout="centered")
st.title("Data Science Academy - Projeto 7")
st.title("🤖 Sistema Web de Suporte Técnico Automatizado com Agentic RAG e LLM Routing")
st.markdown("Faça sua pergunta sobre suporte técnico. O sistema decidirá se busca em documentos internos (RAG) ou na web.")

# Carrega LLM, Retriever e compila o grafo
llm = dsa_carrega_llm_resposta_final()
retriever = dsa_carrega_retriever()
app = dsa_compile_graph()

# Input do usuário
user_query = st.text_input("Sua pergunta:", key = "query_input")

# Botão de envio
if st.button("Buscar Resposta", key = "submit_button"):
    
    if user_query:
        
        with st.spinner("Processando sua consulta..."):
            
            try:
                inputs = {"query": user_query}

                # Executa o grafo (Agente de IA)
                final_state = app.invoke(inputs) 

                st.subheader("Resposta:")
                st.markdown(final_state.get("final_answer", "Não foi possível gerar uma resposta."))
                st.info(f"Fonte utilizada (decidido pelo roteador): {final_state.get('source_decision', 'N/A')}")

            except Exception as e:
                st.error(f"Ocorreu um erro ao processar sua consulta: {e}")
    else:
        st.warning("Por favor, digite sua pergunta.")

# Barra lateral com instruções de uso
st.sidebar.title("Instruções")
st.sidebar.write("""
    - Digite perguntas específicas sobre sua dúvida.
    - O sistema vai "raciocinar" e usar a base de dados do RAG para gerar respostas customizadas ou pesquisar na web.
    - Documentos, manuais e procedimentos complementares podem ser usados para aperfeiçoar o sistema de RAG.
    - IA Generativa comete erros. SEMPRE valide as respostas.
""")

# Botão de suporte na barra lateral que exibe mensagem ao clicar
if st.sidebar.button("Suporte"):
    st.sidebar.write("Dúvidas? Envie um e-mail para: suporte@datascienceacademy.com.br")




    
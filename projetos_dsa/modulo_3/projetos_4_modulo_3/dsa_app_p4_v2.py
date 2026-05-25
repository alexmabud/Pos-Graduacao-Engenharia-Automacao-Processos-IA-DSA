# Projeto 4 - Encadeamento de Prompts, Raciocínio, CoT e Agentic RAG em Contexto Multi-Agentes Para App de Análise de Contratos

# Importar módulo para interação com o sistema operacional
import os

# Importar Streamlit para construção da interface web
import streamlit as st

# Importar função para carregar variáveis de ambiente do arquivo .env
from dotenv import load_dotenv

# Importar classes para criar o grafo de agentes
from langgraph.graph import StateGraph, END

# Importar agentes especializados para processamento de documentos, raciocínio e meta-análise
from agentes.dsa_document_agente import DocumentAgent
from agentes.dsa_reasoning_agente import ReasoningAgent
from agentes.dsa_meta_agente import MetaAgent

# Importar utilitários para recuperação de documentos e geração de embeddings
from utilitarios.retriever import Retriever
from utilitarios.embeddings import Embeddings

# Importar tipos para definir a estrutura do estado
from typing import TypedDict, List

# Resolver incompatibilidade entre Streamlit e PyTorch
import torch
torch.classes.__path__ = []

# Configurar título, ícone e layout da página Streamlit
st.set_page_config(page_title = "Data Science Academy", page_icon = ":100:", layout = "centered")

# Carregar variáveis de ambiente a partir do arquivo .env
load_dotenv()

# Obter a chave da API Groq das variáveis de ambiente
api_key_groq = os.getenv("GROQ_API_KEY")

# Inicializar modelo para geração de embeddings
embedding_model = Embeddings()

# Inicializar Retriever usando o modelo de embeddings
retriever = Retriever(embedding_model)

# Carregar documentos para o Retriever
retriever.dsa_carrega_documentos("dados/documentos/")

# Construir o índice vetorial para recuperação eficiente
retriever.dsa_cria_vectordb()

# Definir estrutura do estado compartilhado entre agentes
class AgentState(TypedDict):
    query: str
    documents: List[str]
    summary: str
    reasoning: str
    final_answer: str

# Função que processa a consulta do usuário integrando múltiplos agentes
def dsa_processa_query(query):

    # Inicializar os agentes
    document_agent = DocumentAgent(api_key_groq)
    reasoning_agent = ReasoningAgent(api_key_groq)
    meta_agent = MetaAgent(api_key_groq)

    # Recuperar documentos relevantes para a consulta
    documents = retriever.dsa_retrieve(query)

    # Gerar resumo dos documentos recuperados
    summary = document_agent.dsa_sumariza_documentos(documents, query)
    st.write("\n**Resumo dos Documentos:**", summary)

    # Gerar raciocínio baseado no resumo obtido
    reasoning = reasoning_agent.dsa_gera_raciocinio(summary, query)
    st.write("\n**Raciocínio:**", reasoning)

    # Gerar a resposta final combinando resumo e raciocínio
    final_answer = meta_agent.dsa_gera_resposta_final(summary, reasoning, query)
    st.write("\n**Resposta Final:**", final_answer)

# Definição da interface principal com Streamlit
def main():

    # Exibir título e subtítulo na interface
    st.title("DSA - Projeto 4")
    st.subheader("Encadeamento de Prompts, Raciocínio, CoT e Agentic RAG em Contexto Multi-Agentes Para App de Análise de Contratos")

    # Barra lateral com instruções de uso
    st.sidebar.title("Instruções")
    st.sidebar.write("""
    - Digite perguntas específicas relacionadas aos documentos pdf de contratos para obter respostas detalhadas.
    - O sistema de Multi-Agentes de IA vai "raciocinar" e usar a base de dados do RAG para gerar respostas customizadas.
    - Documentos, contratos e procedimentos complementares podem ser usados para aperfeiçoar o sistema de RAG.
    - IA Generativa comete erros. SEMPRE valide as respostas.
    """)

    # Botão de suporte na barra lateral
    if st.sidebar.button("Suporte"):
        st.sidebar.write("Dúvidas? Envie um e-mail para: suporte@datascienceacademy.com.br")

    # Campo para inserir a pergunta do usuário
    query = st.text_input("Digite sua pergunta:")

    # Botão para submeter a pergunta
    if st.button("Enviar"):

        # Verificar se uma pergunta foi inserida
        if query:
            dsa_processa_query(query)
        else:
            st.warning("Por favor, insira uma pergunta.")

# Execução principal da aplicação Streamlit
if __name__ == "__main__":
    main()



# Projeto 4 - Encadeamento de Prompts, Raciocínio, CoT e Agentic RAG em Contexto Multi-Agentes Para App de Análise de Contratos

# Importar módulo para interação com sistema operacional
import os

# Importar função para carregar variáveis de ambiente de arquivo .env
from dotenv import load_dotenv

# Importar classes e constantes para construção do grafo de agentes
from langgraph.graph import StateGraph, END

# Importar agentes especializados para processamento de documentos, raciocínio e meta-análise
from agentes.dsa_document_agente import DocumentAgent
from agentes.dsa_reasoning_agente import ReasoningAgent
from agentes.dsa_meta_agente import MetaAgent

# Importar utilitários para recuperação de documentos relevantes e geração de embeddings
from utilitarios.retriever import Retriever
from utilitarios.embeddings import Embeddings

# Importar tipos para definir a estrutura do estado
from typing import TypedDict, List

# Carregar variáveis de ambiente definidas no arquivo .env
load_dotenv()

# Obter a chave da API Groq das variáveis de ambiente
api_key_groq = os.getenv("GROQ_API_KEY")

# Inicializar o modelo responsável por gerar embeddings
embedding_model = Embeddings()

# Inicializar o Retriever usando o modelo de embeddings
retriever = Retriever(embedding_model)

# Carregar documentos de diretório específico
retriever.dsa_carrega_documentos("dados/documentos/")

# Construir o índice vetorial para recuperação de documentos
retriever.dsa_cria_vectordb()

# Definir a estrutura do estado compartilhado entre os agentes
class AgentState(TypedDict):
    query: str
    documents: List[str]
    summary: str
    reasoning: str
    final_answer: str

# Função que representa o nó responsável por recuperar e resumir documentos
def node_document_agent(state: AgentState) -> dict:

    # Inicializar o agente responsável pela manipulação dos documentos
    agent = DocumentAgent(api_key_groq)

    # Recuperar documentos relacionados à consulta
    documents = retriever.dsa_retrieve(state['query'])

    # Gerar resumo dos documentos recuperados com base na consulta
    summary = agent.dsa_sumariza_documentos(documents, state['query'])

    # Exibir resumo gerado
    print("\n[Resumo Documentos]:", summary)

    # Retornar documentos recuperados e resumo para atualização do estado
    return {'documents': documents, 'summary': summary}

# Função que representa o nó responsável por realizar o raciocínio com base no resumo
def node_reasoning_agent(state: AgentState) -> dict:

    # Inicializar o agente responsável pelo raciocínio
    agent = ReasoningAgent(api_key_groq)

    # Gerar raciocínio com base no resumo e na consulta
    reasoning = agent.dsa_gera_raciocinio(state['summary'], state['query'])

    # Exibir raciocínio gerado
    print("\n[Raciocínio]:", reasoning)

    # Retornar raciocínio gerado para atualização do estado
    return {'reasoning': reasoning}

# Função que representa o nó responsável por gerar a resposta final integrando resumo e raciocínio
def node_meta_agent(state: AgentState) -> dict:

    # Inicializar o agente meta responsável pela resposta final
    agent = MetaAgent(api_key_groq)

    # Gerar resposta final com base no resumo, raciocínio e consulta inicial
    final_answer = agent.dsa_gera_resposta_final(state['summary'], state['reasoning'], state['query'])

    # Exibir resposta final gerada
    print("\n[Resposta Final]:", final_answer)

    # Retornar resposta final para atualização do estado
    return {'final_answer': final_answer}

# Inicializar o grafo de agentes com o estado definido
workflow = StateGraph(AgentState)

# Adicionar nós ao grafo de agentes
workflow.add_node("document_agent", node_document_agent)
workflow.add_node("reasoning_agent", node_reasoning_agent)
workflow.add_node("meta_agent", node_meta_agent)

# Definir ponto de entrada do fluxo
workflow.set_entry_point("document_agent")

# Definir transições entre os nós do grafo
workflow.add_edge("document_agent", "reasoning_agent")
workflow.add_edge("reasoning_agent", "meta_agent")
workflow.add_edge("meta_agent", END)

# Compilar o grafo em uma aplicação executável
dsa_workflow_app = workflow.compile()

# Execução principal do script
if __name__ == "__main__":

    print("\nProjeto 4 - Encadeamento de Prompts, Raciocínio, CoT e Agentic RAG em Contexto Multi-Agentes Para App de Análise de Contratos")

    # Solicitar consulta ao usuário
    query = input("\nDigite sua pergunta: ")

    # Criar estado inicial com a consulta inserida pelo usuário
    initial_state = AgentState(query = query, documents = [], summary = "", reasoning = "", final_answer = "")

    # Invocar o grafo de agentes com o estado inicial
    dsa_workflow_app.invoke(initial_state)

    print("\nProcessamento Concluído. Obrigado DSA!\n")

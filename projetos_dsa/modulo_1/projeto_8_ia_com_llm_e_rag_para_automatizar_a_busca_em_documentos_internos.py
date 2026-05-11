# Projeto 8 - IA com LLM e RAG Para Automatizar a Busca em Documentos Internos da Empresa

# Imports

# Bibliotecas padrão
import warnings
from pathlib import Path

# Filtra warnings
warnings.filterwarnings('ignore')

# Biblioteca para criar aplicações web interativas
import streamlit as st

# LangChain - Embeddings e utilities
from langchain_community.embeddings import HuggingFaceEmbeddings

# Llama Index - LLM e componentes para RAG
from llama_index.llms.ollama import Ollama
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings


# Configurações da página
st.set_page_config(page_title = "DSA Projeto 8", page_icon = ":mag_right:", layout = "wide")

# Título e subtítulo da aplicação
st.title("🔍 Busca Inteligente em Documentos Internos")
st.subheader("LLMs e RAG Para Automatizar a Busca em Documentos Internos da Empresa")

# Texto de introdução
st.markdown("""
Bem-vindo ao sistema de busca automatizada para documentos internos da empresa! 
Com o uso de Inteligência Artificial, você pode realizar consultas rápidas e obter respostas detalhadas baseadas nos documentos disponíveis.
""")

# Adiciona uma barra lateral com instruções
with st.sidebar:
    st.header("Instruções")
    st.markdown("""
    1. Digite sua pergunta no campo ao lado.
    2. Aguarde enquanto o assistente processa sua consulta.
    3. Receba uma resposta detalhada baseada nos documentos da empresa.
    4. Sistemas de IA podem cometer erros.
    5. Sempre verifique as respostas.
    """)
    st.write("Exemplos de perguntas:")
    st.write("- Como é feita a coleta de informações de ponto e frequência?")
    st.write("- Quando o departamento financeiro efetua o pagamento ao fornecedor?")
    st.write("- Por que usar o método FIFO (First In, First Out) no processo de logística?")

    # Rodapé da aplicação
    st.markdown("""
    ---
    🧠 Data Science Academy - Projeto 8
    """)

# Inicializa a sessão de mensagens se não existir
if "messages" not in st.session_state.keys():  
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Como posso ajudar? Digite sua pergunta abaixo."}]

# Define o LLM com cache e parâmetros otimizados
@st.cache_resource
def load_llm():
    return Ollama(
        model = "llama3.2",
        request_timeout = 300.0,
        temperature = 0.1,
        context_window = 2048,
        num_output = 512
    )

llm = load_llm()

# Define o modelo de embeddings com cache (usando modelo mais rápido)
@st.cache_resource
def load_embeddings():
    return HuggingFaceEmbeddings(
        model_name = "sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs = {'device': 'cpu'},
        encode_kwargs = {'normalize_embeddings': True}
    )

embed_model = load_embeddings()

# Função para o Módulo de RAG com LlamaIndex, cacheada pelo Streamlit
@st.cache_resource(show_spinner = False)
def dsa_modulo_rag():

    # Exibe um spinner durante o carregamento
    with st.spinner(text = "Carregando e indexando os documentos Streamlit – aguarde! Isso deve levar de 1 a 2 minutos."):  

        # Lê documentos do diretório especificado
        docs_path = r"C:\Users\User\OneDrive\Documentos\Python\Dev_Python\Abud Python Learning\DSA\Módulo_1-Automação-Excel-e-Engenharia-de-Dados\11_automacao_de_processos_com_inteligencia_artificial_e_llms\documentos"
        reader = SimpleDirectoryReader(input_dir = docs_path, recursive = True)  
        
        # Carrega os dados dos documentos
        docs = reader.load_data()  
        
        # Configura o LLM nos settings globais
        Settings.llm = llm

        # Configura o modelo de embeddings nos settings globais
        Settings.embed_model = embed_model

        # Configura o tamanho dos chunks para melhor performance
        Settings.chunk_size = 512
        Settings.chunk_overlap = 50

        # Cria um índice de vetores a partir dos documentos
        index = VectorStoreIndex.from_documents(docs, show_progress=True)  
        
        # Retorna o índice criado
        return index  

# Carrega o índice de dados
index = dsa_modulo_rag() 


# Construindo o Motor de Execução da App com RAG
# Este código verifica se um motor de chat já está inicializado na sessão do Streamlit. 
# Se não estiver, ele o inicializa com as configurações do banco vetorial e o armazena no session_state para uso contínuo durante a sessão do usuário.
# chat_mode = "condense_question" gera um pergunta condensada sendo um modo de chat simples criado em cima de um mecanismo de consulta sobre seus dados.
# Essa abordagem funciona para perguntas diretamente relacionadas à base de conhecimento. 
# Como ele sempre consulta a base de conhecimento, pode ter dificuldade em responder a metaperguntas como "o que eu perguntei a você antes?"
# https://docs.llamaindex.ai/en/stable/examples/chat_engine/chat_engine_condense_question/
if "chat_engine" not in st.session_state.keys():

    # Inicializa o motor de chat com configurações otimizadas
    st.session_state.chat_engine = index.as_chat_engine(
        chat_mode = "condense_question",
        verbose = False,
        similarity_top_k = 2,  # Retorna apenas os 2 documentos mais relevantes
        streaming = False
    )  

# Verifica se há uma entrada de chat do usuário
if prompt := st.chat_input("Sua pergunta"):  

    # Adiciona a mensagem do usuário ao estado da sessão
    st.session_state.messages.append({"role": "user", "content": prompt})  

# Exibe as mensagens na interface de chat
for message in st.session_state.messages: 

    # Cria um componente de mensagem na interface 
    with st.chat_message(message["role"]):  

        # Exibe o conteúdo da mensagem
        st.write(message["content"])  

# Se a última mensagem não for do assistente, gera uma resposta
if st.session_state.messages[-1]["role"] != "assistant":

    # Cria um componente de mensagem para o assistente
    with st.chat_message("assistant"):

        # Exibe um spinner enquanto pensa
        with st.spinner("Pensando..."):

            try:
                # Obtém a pergunta do usuário
                user_message = st.session_state.messages[-1]["content"]

                # Gera uma resposta usando o motor de chat
                response = st.session_state.chat_engine.chat(user_message)

                # Exibe a resposta gerada
                st.write(response.response)

                # Adiciona a mensagem do assistente ao estado da sessão
                st.session_state.messages.append({"role": "assistant", "content": response.response})

            except Exception as e:
                error_message = f"⚠️ Erro ao processar a consulta: {str(e)}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})
# Projeto 3 - Re-Ranking, Agentic RAG com LangGraph e LM Studio Para Assistente de Processo de Licitação

# Biblioteca para manipulação de arquivos JSON
import json 

# Função para carregar o modelo de embeddings pré-treinado
from langchain_huggingface import HuggingFaceEmbeddings  

# Banco de dados vetorial
from langchain_chroma import Chroma  

# Carregadores de documentos
from langchain_community.document_loaders import DirectoryLoader, JSONLoader 

# Divisor de textos em chunks
from langchain.text_splitter import RecursiveCharacterTextSplitter  

# Definição do diretório onde os dados de origem estão armazenados
dsa_diretorio_dados = "dados_origem"

# Definição do diretório onde o banco de dados vetorial será armazenado
dsa_diretorio_vectordb = "rag/chroma_db"

# Variável para armazenar o banco de dados vetorial
dsavectordb = None

# Função para criar o banco de dados vetorial a partir dos documentos processados
def dsa_func_cria_vectordb():

    # Mensagem informando o início do processo
    print("\nGerando as Embeddings. Aguarde...")
    
    # Definição do esquema de conversão para o JSONLoader
    jq_schema = 'to_entries | map(.key + ": " + .value) | join("\\n")'
    
    # Carregamento dos arquivos JSON do diretório especificado
    loader = DirectoryLoader(
        dsa_diretorio_dados,                      # Diretório onde os arquivos JSON de origem estão armazenados
        glob = "*.json",                          # Padrão de arquivos a serem carregados
        loader_cls = JSONLoader,                  # Classe de carregamento de JSON
        loader_kwargs = {"jq_schema": jq_schema}  # Configuração para transformar os dados JSON
    )
    
    # Carrega os documentos a partir do diretório
    documents = loader.load()
    
    # Verifica se há documentos carregados, caso contrário, encerra a função
    if not documents:
        print("Nenhum documento encontrado.")  
        return  
    
    # Define um divisor de texto para segmentar os documentos em partes menores
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,   # Define o tamanho máximo de cada chunk
        chunk_overlap = 50  # Define a sobreposição entre os chunks para manter contexto
    )
    
    # Divide os documentos em chunks menores
    chunks = text_splitter.split_documents(documents)
    
    # Nome do modelo de embeddings utilizado
    # https://huggingface.co/BAAI/bge-base-en
    model_name = "BAAI/bge-base-en"
    
    # Parâmetros para a geração dos embeddings
    # Define a normalização dos embeddings para cálculo de similaridade
    encode_kwargs = {'normalize_embeddings': True}  
    
    # Instancia o modelo de embeddings
    embedding_model = HuggingFaceEmbeddings(
        model_name = model_name,           # Modelo escolhido
        model_kwargs = {'device': 'cpu'},  # Define a execução na CPU
        encode_kwargs = encode_kwargs      # Configuração dos embeddings
    )
    
    # Criação do banco de dados vetorial a partir dos documentos processados
    dsavectordb = Chroma.from_documents(
        chunks,                                     # Chunks gerados a partir dos documentos
        embedding_model,                            # Modelo de embeddings utilizado
        persist_directory = dsa_diretorio_vectordb  # Diretório onde o banco de dados vetorial será armazenado
    )
    
    # Mensagem informando que o banco de dados vetorial foi criado com sucesso
    print("\nBanco de Dados Vetorial do RAG Criado com Sucesso.\n")

# Chamada da função para gerar o banco de dados vetorial
dsa_func_cria_vectordb()






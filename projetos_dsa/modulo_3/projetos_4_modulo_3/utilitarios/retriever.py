# Projeto 4 - Encadeamento de Prompts, Raciocínio, CoT e Agentic RAG em Contexto Multi-Agentes Para App de Análise de Contratos

# Importar módulo para interação com sistema operacional
import os

# Importar divisor de texto para fragmentar documentos grandes
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Importar carregador de documentos PDF
from langchain_community.document_loaders import PyMuPDFLoader

# Importar FAISS para criação de índice vetorial
from langchain_community.vectorstores import FAISS

# Definir classe Retriever para carregar e recuperar documentos
class Retriever:

    # Inicializar classe com modelo de embedding fornecido
    def __init__(self, embedding):
        
        # Atribuir modelo de embedding à instância da classe
        self.embedding = embedding.get_embedding_model()
        
        # Inicializar lista para armazenar documentos carregados
        self.documents = []
        
        # Inicializar variável para armazenar o índice vetorial
        self.vector_store = None

    # Carregar documentos PDF do caminho especificado
    def dsa_carrega_documentos(self, documents_path):
        
        # Iterar sobre os arquivos no diretório fornecido
        for filename in os.listdir(documents_path):
            
            # Verificar se o arquivo tem extensão .pdf
            if filename.endswith(".pdf"):
                
                # Inicializar carregador de documentos PDF com o caminho do arquivo
                loader = PyMuPDFLoader(os.path.join(documents_path, filename))
                
                # Carregar o conteúdo do documento PDF
                loaded_docs = loader.load()
                
                # Adicionar documentos carregados à lista de documentos
                self.documents.extend(loaded_docs)

    # Construir índice vetorial utilizando fragmentos dos documentos
    def dsa_cria_vectordb(self):
        
        # Inicializar o divisor de texto com tamanho e sobreposição de fragmentos
        splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)
        
        # Fragmentar os documentos carregados
        docs_split = splitter.split_documents(self.documents)
        
        # Criar o índice vetorial a partir dos documentos fragmentados e embedding
        self.vector_store = FAISS.from_documents(docs_split, self.embedding)

    # Recuperar documentos mais relevantes a partir da consulta do usuário
    def dsa_retrieve(self, query, k = 5):
        
        # Verificar se o índice vetorial foi inicializado
        if not self.vector_store:
            
            # Lançar erro se o índice vetorial não estiver disponível
            raise ValueError("Vector store não está inicializada.")
        
        # Realizar busca de similaridade no índice vetorial com a consulta fornecida
        docs = self.vector_store.similarity_search(query, k = k)
        
        # Retornar os documentos mais relevantes encontrados
        return docs




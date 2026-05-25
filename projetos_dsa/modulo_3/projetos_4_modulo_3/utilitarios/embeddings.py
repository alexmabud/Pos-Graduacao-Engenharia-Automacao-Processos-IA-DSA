# Projeto 4 - Encadeamento de Prompts, Raciocínio, CoT e Agentic RAG em Contexto Multi-Agentes Para App de Análise de Contratos

# Import para interação com o sistema operacional
import os

# Import para geração de embeddings
from langchain_huggingface import HuggingFaceEmbeddings

# Desativar paralelismo na tokenização para garantir compatibilidade entre sistemas operacionais
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Definir classe para gerenciar embeddings
class Embeddings:
    
    # Inicializar classe com modelo específico de embeddings
    def __init__(self):

        # Nome do modelo
        model_name = "BAAI/bge-base-en"

        # Cria instância da classe
        self.model = HuggingFaceEmbeddings(model_name = model_name)

    # Método para retornar o modelo de embeddings inicializado
    def get_embedding_model(self):
        return self.model

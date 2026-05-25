# Projeto 4 - Encadeamento de Prompts, Raciocínio, CoT e Agentic RAG em Contexto Multi-Agentes Para App de Análise de Contratos

# Importar cliente Groq para interação com modelos de IA
from groq import Groq

# Definir classe para o agente especializado em documentos
class DocumentAgent:

    # Inicializar a classe com a chave da API Groq
    def __init__(self, api_key):
        self.client = Groq(api_key = api_key)

    # Método para gerar um resumo dos documentos com base na consulta
    def dsa_sumariza_documentos(self, documents, query):

        # Concatenar conteúdo dos documentos em um único contexto textual
        context = "\n\n".join([doc.page_content for doc in documents])

        # Definir mensagens para a solicitação ao modelo de IA
        messages = [
            {"role": "system", "content": "Você resume documentos com precisão."},
            {"role": "user", "content": f"Documentos: {context}\n\nResponda brevemente à pergunta: {query}"}
        ]

        # Criar a solicitação ao modelo
        completion = self.client.chat.completions.create(model = "llama-3.1-8b-instant",
                                                         messages = messages,
                                                         temperature = 0.7,
                                                         max_tokens = 1024)

        # Retornar o resumo gerado pelo modelo, removendo espaços adicionais
        return completion.choices[0].message.content.strip()

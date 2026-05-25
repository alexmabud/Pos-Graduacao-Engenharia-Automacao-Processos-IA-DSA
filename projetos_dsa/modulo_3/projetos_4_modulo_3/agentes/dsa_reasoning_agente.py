# Projeto 4 - Encadeamento de Prompts, Raciocínio, CoT e Agentic RAG em Contexto Multi-Agentes Para App de Análise de Contratos

# Importar cliente Groq para interação com modelos de IA
from groq import Groq

# Definir classe para o agente especializado em raciocínio lógico
class ReasoningAgent:

    # Inicializar a classe com a chave da API Groq
    def __init__(self, api_key):
        self.client = Groq(api_key = api_key)

    # Método para gerar raciocínio lógico a partir do resumo e da consulta
    def dsa_gera_raciocinio(self, summary, query):

        # Definir mensagens para enviar ao modelo de IA
        messages = [
            {"role": "system", "content": "Você é especialista em raciocínio lógico sobre textos."},
            {"role": "user", "content": f"Com base no resumo: {summary}\n\nFaça uma análise crítica para responder à pergunta: {query}"}
        ]

        # Criar solicitação ao modelo usando parâmetros específicos
        completion = self.client.chat.completions.create(model = "llama-3.3-70b-versatile",
                                                         messages = messages,
                                                         temperature = 0.7,
                                                         max_tokens = 1024)

        # Retornar o raciocínio lógico gerado pelo modelo, removendo espaços adicionais
        return completion.choices[0].message.content.strip()


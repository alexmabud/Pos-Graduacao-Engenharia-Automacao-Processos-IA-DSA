# Projeto 4 - Encadeamento de Prompts, Raciocínio, CoT e Agentic RAG em Contexto Multi-Agentes Para App de Análise de Contratos

# Importar cliente Groq para interação com modelos de IA
from groq import Groq

# Definir classe para o agente meta, responsável pela resposta final
class MetaAgent:

    # Inicializar a classe com a chave da API Groq
    def __init__(self, api_key):
        self.client = Groq(api_key = api_key)

    # Método para gerar a resposta final combinando resumo e raciocínio
    def dsa_gera_resposta_final(self, summary, reasoning, query):

        # Definir mensagens para enviar ao modelo de IA
        messages = [
            {"role": "system", "content": "Você gera respostas claras e detalhadas consolidando informações."},
            {"role": "user", "content": f"Pergunta original: {query}\n\nResumo: {summary}\n\nRaciocínio lógico: {reasoning}\n\nForneça a resposta consolidada e detalhada:"}
        ]

        # Criar a solicitação ao modelo, configurando o streaming para obter resposta incremental
        completion = self.client.chat.completions.create(model = "qwen/qwen3-32b",
                                                         messages = messages,
                                                         temperature = 0.7,
                                                         max_tokens = 1024,
                                                         stream = True)

        # Inicializar variável para armazenar a resposta final
        resposta_final = ""

        # Iterar sobre a resposta em chunks (partes) recebidas do modelo
        for chunk in completion:
            chunk_content = chunk.choices[0].delta.content or ""
            print(chunk_content, end="", flush = True)
            resposta_final += chunk_content

        # Retornar a resposta final consolidada
        return resposta_final

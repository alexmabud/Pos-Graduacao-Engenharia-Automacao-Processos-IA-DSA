# Projeto 2 - Construção de Multi-Agentes de IA com CrewAI e Deploy via API com Docker

# Imports
import requests
import json

print("\nO Time de Multi-Agentes de IA Está Processando Sua Requisição. Aguarde...\n")

# URL da API
API_URL = "http://localhost:8000/execute"

# Tópico a ser pesquisado
data = {"topic": "Jurisprudência de prisão em segunda instância no Brasil"}

# Faz a requisição POST à API
response = requests.post(API_URL, json=data)

# Verifica se a requisição foi bem-sucedida
if response.status_code == 200:
    resultado = response.json()
    
    # Obtém o relatório gerado
    if "result" in resultado and "raw" in resultado["result"]:
        relatorio = resultado["result"]["raw"]
        
        print("\n*****Relatório Gerado:*****\n")
        print(relatorio)
    
    else:
        print("Erro: Resposta inesperada da API.")
else:
    print(f"Erro na requisição: {response.status_code} - {response.text}")

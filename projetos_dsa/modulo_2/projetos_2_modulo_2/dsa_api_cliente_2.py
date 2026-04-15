# Projeto 2 - SQL, LLM e RAG Para Sistema de Recomendação Personalizado Por IA via API
# Módulo Para Executar o Sistema de Recomendação com SQL, LLM e RAG

# Imports
import requests
from urllib.parse import quote

# URL da API
url = 'http://127.0.0.1:8000/dsa_llm_recomenda_tratamento/'

# Solicitando o nome e o ID do paciente ao usuário
nome_paciente = input("Digite o nome do paciente para o qual você gostaria de ter recomendações de tratamento: ")
id_paciente = input("Digite o ID do paciente: ")  

# Codifica o nome para uso com a URL
encoded_nome_paciente = quote(nome_paciente)  

# Formatando a URL com o nome e o ID do paciente codificado
full_url = f"{url}?nome_paciente={encoded_nome_paciente}&id_paciente={id_paciente}"

# Exemplo: http://127.0.0.1:8000/dsa_llm_recomenda_tratamento/?nome_paciente=Bob&id_paciente=1

# Enviando a requisição GET
response = requests.get(full_url)

# Verificando a resposta
if response.status_code == 200:
    data = response.json()
    nome_paciente = data['nome_paciente']
    recomendacoes = data['recomendações']
    print(f"Successo:\n\nPaciente: {nome_paciente}\n\nRecomendações:\n{recomendacoes}")
else:
    print("Falha:", response.status_code, response.text)



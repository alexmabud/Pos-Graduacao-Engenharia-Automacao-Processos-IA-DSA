# Projeto 2 - SQL, LLM e RAG Para Sistema de Recomendação Personalizado Por IA via API
# Módulo Para Carregar o Banco de Dados do RAG

# Imports
import requests

# URL da API
url = 'http://127.0.0.1:8000/dsa_cadastra_paciente'

# Solicitando os dados ao usuário
nome_paciente = input("Digite o nome do paciente: ")
idade = int(input("Digite a idade do paciente: "))
genero = input("Digite o gênero do paciente (Masculino/Feminino/Outro): ")

# Coletando múltiplos sintomas e tratando a entrada como uma lista
sintomas_input = input("Digite os sintomas do paciente, separados por vírgula (ex: tosse, febre, pressão alta): ")
sintomas = [sintoma.strip() for sintoma in sintomas_input.split(',')]

# Dados a serem enviados como JSON
dsa_dados = {"nome_paciente": nome_paciente,
             "idade": idade,
             "genero": genero,
             "sintomas": sintomas
}

# Enviando a requisição POST
response = requests.post(url, json = dsa_dados)

# Verificando a resposta
if response.status_code == 200:
    print("Sucesso:", response.json())
else:
    print("Falha:", response.status_code, response.text)





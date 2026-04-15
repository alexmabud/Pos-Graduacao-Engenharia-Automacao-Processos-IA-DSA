# Projeto 2 - SQL, LLM e RAG Para Sistema de Recomendação Personalizado Por IA via API
# Módulo de RAG Para o Sistema de Recomendação via API

# Imports
import os
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from openai import OpenAI
from asgiref.wsgi import WsgiToAsgi
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Cria a instância da app
app = FastAPI()

# Cria a instância do LLM (Large Language Model)
llm_dsa = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# Função para abrir a conexão com o banco de dados
def dsa_db_conn():

    # Conecta ao banco de dados SQLite (cria o banco na primeira execução)
    conn = sqlite3.connect('dsa_db_p2.db')

    # Configura para retornar resultados como dicionários
    conn.row_factory = sqlite3.Row

    return conn

# Função para criar as tabelas no banco de dados
def dsa_cria_tabela():

    # Abre a conexão com o banco de dados
    conn = dsa_db_conn()
    cursor = conn.cursor()

    # Cria a tabela de dados dos pacientes, se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dsa_tb_dados_pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_paciente TEXT NOT NULL,
            idade INTEGER NOT NULL,
            genero TEXT NOT NULL,
            sintomas TEXT NOT NULL
        );
    ''')

    # Salva as mudanças no banco de dados
    conn.commit()

    # Fecha a conexão com o banco de dados
    conn.close()

# Evento de inicialização para criar as tabelas no startup
@app.on_event("startup")
async def startup_event():
    dsa_cria_tabela()

# Endpoint para cadastrar um novo paciente
# Veja a explicação no videobook do Capítulo 6
@app.post("/dsa_cadastra_paciente")
async def dsa_cadastra_paciente(json_data: dict):

    # Abre a conexão com o banco de dados
    conn = dsa_db_conn()
    cursor = conn.cursor()

    # Obtém os dados do paciente do JSON recebido
    nome_paciente = json_data.get('nome_paciente')
    idade = json_data.get('idade')
    genero = json_data.get('genero')
    sintomas = json_data.get('sintomas')

    # Verifica se todos os dados necessários foram fornecidos
    if not all([nome_paciente, idade, genero, sintomas]):
        raise HTTPException(status_code = 400, detail = "Dados fornecidos de forma incompleta.")

    # Concatena os sintomas em uma string separada por vírgulas
    sintomas_str = ', '.join(sintomas)

    # Verifica se o paciente já está cadastrado no banco de dados e retorna 1 registro (se houver mais de 1)
    cursor.execute("SELECT * FROM dsa_tb_dados_pacientes WHERE nome_paciente = ? AND idade = ? AND genero = ?", (nome_paciente, idade, genero))
    existing_paciente = cursor.fetchone()

    if existing_paciente:

        # Atualiza os sintomas do paciente existente
        id_paciente = existing_paciente['id']
        cursor.execute("UPDATE dsa_tb_dados_pacientes SET sintomas = sintomas || ', ' || ? WHERE id = ?", (sintomas_str, id_paciente))

    else:

        # Insere um novo registro de paciente
        cursor.execute("INSERT INTO dsa_tb_dados_pacientes (nome_paciente, idade, genero, sintomas) VALUES (?, ?, ?, ?)", (nome_paciente, idade, genero, sintomas_str))
        id_paciente = cursor.lastrowid

    # Salva as mudanças no banco de dados
    conn.commit()

    # Fecha a conexão com o banco de dados
    conn.close()

    # Retorna uma mensagem de sucesso
    return {"mensagem": "Os dados foram salvos com sucesso.", "id_paciente": id_paciente}

# Endpoint para recomendar tratamento usando LLM
@app.get("/dsa_llm_recomenda_tratamento/")
async def dsa_llm_recomenda_tratamento(nome_paciente: str, id_paciente: int):

    # Abre a conexão com o banco de dados
    conn = dsa_db_conn()
    cursor = conn.cursor()

    # Busca os dados do paciente pelo nome e ID
    cursor.execute("SELECT * FROM dsa_tb_dados_pacientes WHERE nome_paciente = ? AND id = ?", (nome_paciente, id_paciente))
    paciente = cursor.fetchone()
    conn.close()

    if paciente:

        # Prepara o texto de prompt para o LLM
        prompt_text = f"Paciente: {paciente['nome_paciente']}\nSintomas: {paciente['sintomas']}\nidade: {paciente['idade']}\ngenero: {paciente['genero']}\nPor favor forneça recomendações de tratamento."
        print(prompt_text)

        # Faz a solicitação ao LLM para obter recomendações de tratamento
        response = llm_dsa.chat.completions.create(
            model = "gpt-4o",
            messages = [
                {"role": "system", "content": "Você é um especialista médico capaz de recomendar tratamentos personalizados."},
                {"role": "user", "content": prompt_text}
            ],
            max_tokens = 150,
            n = 1
        )

        # Extrai as recomendações da resposta do LLM
        recommendations = response.choices[0].message.content

        # Retorna as recomendações
        return {"nome_paciente": paciente['nome_paciente'], "recomendações": recommendations}
    else:
        # Retorna um erro 404 se o paciente não for encontrado
        raise HTTPException(status_code = 404, detail = "Paciente não encontrado")

# Converte o aplicativo WSGI FastAPI para ASGI
# Veja a explicação no videobook do Capítulo 6
asgi_app = WsgiToAsgi(app)




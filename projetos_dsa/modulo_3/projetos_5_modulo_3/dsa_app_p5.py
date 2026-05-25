# Projeto 5 - Construção e Deploy de Routing com Multi-Agentes de IA

# Importar módulo para interagir com sistema operacional
import os

# Importar módulo para lidar com arquivos JSON
import json

# Importar módulo Streamlit para criar interface web
import streamlit as st

# Importar módulo para carregar variáveis de ambiente
from dotenv import load_dotenv

# Importar cliente Groq para usar modelos de IA
from groq import Groq

# Configurar página do Streamlit
st.set_page_config(page_title="Data Science Academy", page_icon=":100:", layout="centered")

# Configurar título da barra lateral do Streamlit
st.sidebar.title("Instruções")

# Exibir instruções para o usuário na barra lateral
st.sidebar.markdown("""
Digite sua pergunta na caixa ao lado e clique no botão **Enviar**.

A aplicação selecionará automaticamente o melhor Agente para responder com base na complexidade da pergunta.

Tipos de perguntas:
- **Factual**: Perguntas curtas e diretas.
- **Pesquisa**: Perguntas que exigem respostas detalhadas.
- **Geral**: Outras consultas.

IA Generativa comete erros. **SEMPRE** use seu conhecimento para verificar as respostas.
""")

# Botão de suporte na barra lateral que exibe mensagem ao clicar
if st.sidebar.button("Suporte"):
    st.sidebar.write("Dúvidas? Envie um e-mail para: suporte@datascienceacademy.com.br")

# Carregar variáveis de ambiente
load_dotenv()

# Carregar configuração dos modelos Groq a partir de arquivo JSON
with open('groq_modelos_config.json', 'r') as file:
    modelos_config = json.load(file)

# Inicializar o cliente Groq com a chave de API carregada das variáveis de ambiente
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Classe para avaliar a intenção da consulta do usuário
class AgenteIntencao:
    @staticmethod
    def avaliar_intencao(consulta):

        # Avalia se a consulta é factual
        if len(consulta.split()) <= 10 and 'Informe' in consulta:
            return 'factual'

        # Avalia se a consulta é do tipo pesquisa
        elif '?' in consulta:
            return 'pesquisa'

        # Caso contrário, considera como consulta geral
        else:
            return 'geral'

# Classe para buscar informação usando o modelo adequado
class AgenteInformacao:
    @staticmethod
    def buscar_informacao(consulta, intencao):

        # Retorna a config de acordo com a intenção do usuário
        config = modelos_config[intencao]

        # Extrai o modelo
        modelo = config["modelo"]

        # Formata o prompt
        prompt_customizado = config["prompt"].format(consulta=consulta)

        # Gera a resposta do LLM
        resposta = client.chat.completions.create(
            messages = [{"role": "user", "content": prompt_customizado}],
            model = modelo,
        )

        return resposta.choices[0].message.content, modelo

# Classe para formular resposta final com base na intenção
class AgenteResposta:
    @staticmethod
    def formular_resposta(informacao, intencao):

        # Formula resposta rápida para consultas factuais
        if intencao == 'factual':
            return f"Resposta rápida: {informacao}"

        # Formula resposta detalhada para consultas de pesquisa
        elif intencao == 'pesquisa':
            return f"Resposta detalhada: {informacao}"

        # Formula resposta geral para outros casos
        else:
            return f"Resposta geral: {informacao}"

# Função principal que obtém resposta com base na consulta
def dsa_obtem_resposta(consulta):

    # Avaliar intenção da consulta
    intencao = AgenteIntencao.avaliar_intencao(consulta)

    # Buscar informação com base na intenção avaliada
    informacao, modelo_usado = AgenteInformacao.buscar_informacao(consulta, intencao)

    # Formular resposta final com base na informação e intenção
    resposta_final = AgenteResposta.formular_resposta(informacao, intencao)

    # Retornar resposta final e modelo usado
    return resposta_final, modelo_usado

# Interface principal do Streamlit
st.title("DSA Projeto 5")
st.subheader("Construção e Deploy de Routing com Multi-Agentes de IA")

# Campo para entrada de texto da consulta do usuário
consulta = st.text_input("Digite sua pergunta:")

# Botão para enviar consulta
if st.button("Enviar"):

    # Verifica se a consulta não está vazia
    if consulta.strip():

        # Obter resposta e modelo utilizado
        resposta, modelo_usado = dsa_obtem_resposta(consulta)

        # Exibir resposta
        st.write(resposta)

        # Exibir modelo utilizado para gerar resposta
        st.caption(f"Modelo utilizado: {modelo_usado}")

    # Exibe aviso caso a consulta esteja vazia
    else:
        st.warning("Por favor, digite uma pergunta antes de enviar.")



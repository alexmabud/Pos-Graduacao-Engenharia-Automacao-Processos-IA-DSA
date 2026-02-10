# Estudo de Caso - Estratégias de RAG e Suas Variantes - Sistema de RAG Local com DeepSeek e Ollama

# Imports
import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains import RetrievalQA
import warnings
warnings.filterwarnings('ignore')

# Configurando o título da página e outras configurações (favicon)
st.set_page_config(page_title = "Data Science Academy", page_icon = ":100:", layout = "centered")

# Título
st.title("Estudo de Caso - Estratégias de RAG e Suas Variantes - Sistema de RAG Local com DeepSeek e Ollama")
st.markdown("---")

# Sidebar com as instruções
with st.sidebar:
    st.header("Instruções")
    st.markdown("""
    1. Faça upload de um arquivo PDF.
    2. Aguarde o carregamento e faça perguntas.
    3. O sistema vai recuperar o conteúdo relevante e a IA vai fornecer uma resposta.
    """)

# Uploader para upload do arquivo pdf
uploaded_file = st.file_uploader("Upload de Documento PDF", type = "pdf")

# Se tiver arquivo iniciamos o processamento
if uploaded_file is not None:

    # Mensagem
    st.success("PDF Carregado com Sucesso! Aguarde o Processamento e Digite Sua Pergunta!")

    # Vamos salvar o arquivo por segurança
    with open("arquivo.pdf", "wb") as f:
        f.write(uploaded_file.getvalue())

    # Lê o arquivo pdf
    loader = PDFPlumberLoader("arquivo.pdf")

    # Carrega o conteúdo do arquivo
    docs = loader.load()

    # Divide os dados de texto em chunks (veja mais detalhes no videobook do Capítulo 3)
    text_splitter = SemanticChunker(HuggingFaceEmbeddings())
    documents = text_splitter.split_documents(docs)

    # Define o modelo de embeddings (veja mais detalhes no videobook do Capítulo 3)
    embedder = HuggingFaceEmbeddings()

    # Cria o banco de dados vetorial em memória (veja mais detalhes no videobook do Capítulo 3)
    dsavectordb = FAISS.from_documents(documents, embedder)

    # Cria o retriever (veja mais detalhes no videobook do Capítulo 3)
    dsaretriever = dsavectordb.as_retriever(search_type = "similarity", search_kwargs = {"k": 2})

    # Cria instância do LLM
    llm = OllamaLLM(model = "deepseek-r1:1.5b")

    # Define o prompt
    prompt = """
    1. Use os seguintes pedaços de contexto para responder à pergunta no final sempre em Português do Brasil.\n
    2. Se você não sabe a resposta, apenas diga "Eu não sei", mas não invente uma resposta.\n
    3. Mantenha a resposta concisa e limitada a 3 ou 4 parágrafos sempre em Português do Brasil.\n
    Contexto: {context}
    Pergunta: {question}
    Resposta:"""

    # Cria o prompt template
    prompt_template_geral = PromptTemplate.from_template(prompt)

    # Cria a cadeia de operações
    llm_chain = LLMChain(llm = llm, prompt = prompt_template_geral, verbose = True)

    # Cria o prompt específico com o contexto
    dsa_prompt = PromptTemplate(input_variables = ["page_content", "source"],
                                template = "Contexto:\ncontent:{page_content}\nsource:{source}")

    # Combina contexto, prompt e LLM chain
    dsa_documents_chain = StuffDocumentsChain(llm_chain = llm_chain,
                                              document_variable_name = "context",
                                              document_prompt = dsa_prompt,
                                              verbose = True)

    # Cria o retrieval de perguntas e respostas
    qa_retrieval = RetrievalQA(combine_documents_chain = dsa_documents_chain,
                               retriever = dsaretriever,
                               verbose = True,
                               return_source_documents = True)

    # User input
    user_input = st.text_input("Digite sua pergunta relacionada ao documento:")

    # Processa a entrada do usuário e gera a resposta
    if user_input:
        with st.spinner("A Inteligência Artificial está processando sua consulta..."):
            try:
                response = qa_retrieval(user_input)["result"]
                st.success("Resposta do DeepSeek:")
                st.write(response)
            except Exception as e:
                st.error(f"Ocorreu um erro: {e}")
else:
    st.info("Faça o upload de um documento PDF para começar.")


# Fim

# Exemplos de perguntas:

# A pandemia do COVID-19 acelerou o ritmo do desenvolvimento digital em todo o mundo?
# Quantos milhões de empregos o Fórum Econômico Mundial estima que podem ser perdidos para a automação nos próximos três anos?
# Qual a habilidade mais importante na era da Inteligência Artificial?






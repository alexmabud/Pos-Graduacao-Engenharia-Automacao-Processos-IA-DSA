# Projeto 7 - Gerenciamento de Memória e Contexto - Sistema de Multi-Agentes de IA com LangGraph Para Automação do CRM e Consulta a Banco de Dados

# Importa a biblioteca os para manipulação de variáveis e caminhos do sistema operacional
import os

# Importa o Streamlit para criação de interface web interativa
import streamlit as st

# Importa sqlite3 para interação com banco de dados SQLite
import sqlite3 

# Importa operator para operações funcionais em estruturas de dados
import operator

# Importa a função load_dotenv para carregar variáveis de ambiente de um arquivo .env
from dotenv import load_dotenv

# Importa Annotated, List e TypedDict para anotações de tipos avançados em Python
from typing import Annotated, List, TypedDict

# Importa o cliente ChatGroq para realizar chamadas ao modelo Groq
from langchain_groq import ChatGroq

# Importa o cliente ChatOpenAI para realizar chamadas ao modelo da OpenAI
from langchain_openai import ChatOpenAI

# Importa classes de mensagem do LangChain para estruturar comunicações entre agentes
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage

# Importa ferramentas de template de prompt do LangChain para construir conversas
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Importa a classe StateGraph e constantes de início/fim para definição de grafos de estados
from langgraph.graph import StateGraph, END, START

# Importa nós de ferramenta predefinidos para uso dentro do grafo de estados
from langgraph.prebuilt import ToolNode

# Importa o decorador tool para registrar funções como ferramentas de agente
from langchain.tools import tool

# Define o nome do arquivo que será utilizado como banco de dados SQLite
DB_FILE = "dsa_crm_database.db" 

# Configura o layout da página no Streamlit com título, ícone e largura do layout
st.set_page_config(page_title="Data Science Academy", page_icon=":100:", layout="wide")

# Exibe os títulos 
st.title("Data Science Academy - Projeto 7")
st.title("🤖 Gerenciamento de Memória e Contexto - Sistema Multi-Agentes de IA com LangGraph Para Automação do CRM e Consulta a Banco de Dados")

# Carrega variáveis de ambiente definidas em arquivo .env
load_dotenv()

# Obtém a chave da API Groq das variáveis de ambiente ou usa string vazia como padrão
groq_api_key = os.getenv("GROQ_API_KEY", "")

# Obtém a chave da API OpenAI das variáveis de ambiente ou usa string vazia como padrão
openai_api_key = os.getenv("OPENAI_API_KEY", "")

# Cria um campo na barra lateral para inserir a chave Groq, ocultando o valor digitado
#groq_api_key = st.sidebar.text_input("🔑 Groq API Key", type = "password", value = default_groq)

# Cria um campo na barra lateral para inserir a chave OpenAI, ocultando o valor digitado
#openai_api_key = st.sidebar.text_input("🔑 OpenAI API Key", type = "password", value = default_openai)

# Verifica se ambas as chaves foram fornecidas; se não, exibe alerta e interrompe a execução
if not groq_api_key or not openai_api_key:

    # Exibe um aviso informando que é necessário definir ambas as chaves para continuar
    st.warning("⚠️ Defina ambas as chaves Groq e OpenAI na barra lateral para continuar.")

    # Interrompe a execução do aplicativo até que as chaves sejam definidas
    st.stop()

# Define um tipo de dicionário para representar o estado do agente com tipagem estática
class AgentState(TypedDict):

    # Declara o campo 'messages' como uma lista de BaseMessage, agregada pelo operador de soma
    messages: Annotated[List[BaseMessage], operator.add]

# Registra a função como ferramenta utilizável pelos agentes
@tool
# Define a função dsa_query_crm_database, que recebe uma string de consulta SQL e retorna uma string com o resultado
def dsa_query_crm_database(sql_query: str) -> str:
    # Docstring que descreve o comportamento e uso da ferramenta
    """
    Executa uma consulta SQL SOMENTE do tipo SELECT no banco de dados CRM SQLite
    e retorna os resultados.
    Usamos esta ferramenta para obter informações sobre clientes ou interações.
    Tabelas disponíveis:
    1. tb_dsa_clientes (colunas: customer_id, name, email, phone, company, status, created_at)
       - status pode ser 'Lead', 'Active', 'Inactive', 'Prospect'
    2. tb_dsa_interacoes (colunas: interaction_id, customer_id, interaction_date, type, notes)
       - type pode ser 'Email', 'Call', 'Meeting', 'Note'
    Importante: Forneça APENAS consultas SQL `SELECT`. Não use `UPDATE`, `DELETE`, `INSERT` ou `DROP`.
    Exemplo de consulta SQL válida:
    'SELECT name, email FROM tb_dsa_clientes WHERE status = \\'Active\\';'
    'SELECT i.interaction_date, i.type, i.notes FROM tb_dsa_interacoes i JOIN tb_dsa_clientes c ON i.customer_id = c.customer_id WHERE c.name = \\'João Silva\\' ORDER BY i.interaction_date DESC;'
    """
    # Exibe no console a query recebida para fins de debug
    print(f"--- Ferramenta dsa_query_crm_database recebendo SQL: {sql_query} ---")

    # Verifica se a consulta começa com SELECT, garantindo segurança
    if not sql_query.strip().upper().startswith("SELECT"):

        # Em caso de tentativa de SQL não-SELECT, exibe erro de segurança
        print("!!! ERRO DE SEGURANÇA: Tentativa de executar SQL não-SELECT !!!")

        # Retorna mensagem de erro ao usuário
        return "Erro: Esta ferramenta só pode executar consultas SELECT."

    # Inicializa a variável de conexão como None
    conn = None

    # Bloco principal de execução da consulta SQL
    try:

        # Verifica se o arquivo de banco de dados existe antes de conectar
        if not os.path.exists(DB_FILE):

             # Retorna mensagem de erro se o arquivo não foi encontrado
             return f"Erro: Arquivo do banco de dados '{DB_FILE}' não encontrado. Execute o script 'create_crm_db.py' primeiro."

        # Abre conexão com o banco de dados SQLite
        conn = sqlite3.connect(DB_FILE)

        # Cria um cursor para executar comandos SQL
        cursor = conn.cursor()

        # Executa a consulta SQL recebida
        cursor.execute(sql_query)

        # Busca todos os resultados retornados pela consulta
        results = cursor.fetchall()

        # Caso não haja resultados, informa ao usuário
        if not results:

            return "Nenhum resultado encontrado para a consulta."

        else:

            # Obtém os nomes das colunas a partir da descrição do cursor
            column_names = [description[0] for description in cursor.description]

            # Cria um cabeçalho com nomes de colunas separados por " | "
            header = " | ".join(column_names)

            # Converte cada linha de resultados em string, separando campos por " | "
            rows_str = [" | ".join(map(str, row)) for row in results]

            # Define número máximo de resultados a exibir
            max_results = 15

            # Monta a saída inicial com quantidade de registros e cabeçalho
            output = f"Resultados da consulta ({len(results)} encontrados):\n{header}\n" + "\n".join(rows_str[:max_results])

            # Se houver mais resultados que o limite, adiciona informação de omissão
            if len(results) > max_results:
                output += f"\n... (mais {len(results) - max_results} resultados omitidos)"

            # Retorna a string formatada com os resultados da consulta
            return output

    # Captura erros específicos de SQLite
    except sqlite3.Error as e:
        
        # Exibe mensagem de erro SQL no console para debug
        print(f"!!! ERRO SQL: {e} ao executar '{sql_query}' !!!")
        
        # Retorna mensagem de erro ao usuário com detalhes do SQLite
        return f"Erro ao executar a consulta SQL: {e}. Verifique a sintaxe da sua consulta e os nomes das tabelas/colunas."
   
    # Captura quaisquer outras exceções inesperadas
    except Exception as e:

        # Exibe mensagem genérica de erro no console para debug
        print(f"!!! ERRO Inesperado na ferramenta: {e} !!!")
        
        # Retorna mensagem de erro genérico ao usuário
        return f"Ocorreu um erro inesperado na ferramenta de banco de dados: {e}"
    
    # Bloco finally executado sempre, para fechar conexão se aberta
    finally:
        
        # Se a conexão foi estabelecida, fecha-a para não deixar recursos abertos
        if conn:
            conn.close()

# Lista de ferramentas
tools = [dsa_query_crm_database]

# Cria o objeto para o nó de ferramenta
tool_node = ToolNode(tools) 

# Define a função que cria um agente “runnable” a partir de um LLM e um prompt de sistema
def dsa_cria_agente_runnable(llm, system_prompt):

    # Cria um template de chat prompt a partir de uma lista de mensagens
    prompt = ChatPromptTemplate.from_messages(
        [
            # Mensagem do sistema contendo as instruções iniciais
            ("system", system_prompt),
            
            # Placeholder para inserir o histórico de mensagens trocadas
            MessagesPlaceholder(variable_name = "messages"),
        ]
    )

    # Associa as ferramentas disponíveis ao LLM, criando um pipeline executável
    agent_runnable = prompt | llm.bind_tools(tools)
    
    # Retorna o agente configurado para execução
    return agent_runnable

# Define a função do nó do agente Groq responsável por interagir com o CRM
def dsa_groq_agent_node(state: AgentState):

    print("\n *** Executando o Nó Groq (CRM) *** \n")

    try:

        # Inicializa o LLM Groq com o modelo, temperatura e chave de API
        llm_groq = ChatGroq(model_name="llama3-8b-8192", temperature=0.2, groq_api_key=groq_api_key) 
        
        # Define o prompt do sistema com instruções para usar a ferramenta CRM
        system_prompt = """Você é um assistente de CRM chamado Groq (modelo Llama3).
        Sua principal função é responder perguntas sobre clientes e interações consultando o banco de dados CRM.
        Use a ferramenta 'dsa_query_crm_database' fornecendo uma consulta SQL SELECT válida para buscar as informações pedidas.
        Consulte a descrição da ferramenta para ver o schema do banco de dados (tabelas: tb_dsa_clientes, tb_dsa_interacoes e suas colunas).
        Seja direto e baseie suas respostas nos dados retornados pela ferramenta. Se a ferramenta retornar um erro, informe o usuário.
        Não invente informações se elas não estiverem no banco de dados.
        """
        
        # Cria um agente executável a partir do LLM e do prompt do sistema
        agent_runnable = dsa_cria_agente_runnable(llm_groq, system_prompt)
        
        # Informa que o agente Groq foi criado e será invocado
        print("Runnable Groq (CRM) criado. Invocando...")
        
        # Invoca o agente com o histórico de mensagens contido no estado
        response = agent_runnable.invoke({"messages": state['messages']})
        
        # Exibe informações sobre o tipo de resposta e parte do seu conteúdo
        print(f"Nó Groq (CRM) Obteve Resposta: Tipo = {type(response)}, Conteúdo = '{response.content[:50]}...'")
        
        # Verifica se a resposta inclui chamadas de ferramentas
        if hasattr(response, 'tool_calls') and response.tool_calls:

            # Exibe quais ferramentas foram acionadas pelo agente
            print(f"Nó Groq (CRM) está chamando a ferramenta: {response.tool_calls}")
        
        # Retorna o dicionário contendo as mensagens de resposta do agente
        return {"messages": [response]}

    except Exception as e:

        # Em caso de exceção, exibe mensagem de erro no console
        print(f"!!! ERRO NO NÓ Groq (CRM): {e} !!!")
        
        # Mostra o erro ao usuário na interface Streamlit
        st.error(f"Ocorreu um erro ao contactar a API Groq: {e}")
        
        # Cria uma mensagem de erro interna para ser retornada pelo nó
        error_msg = AIMessage(content = f"[ERRO INTERNO GROQ]: Não foi possível processar com Groq. Detalhe: {e}", name = "ErroGroq")
        
        # Retorna o dicionário contendo a mensagem de erro
        return {"messages": [error_msg]}

# Define a função do nó do agente OpenAI responsável por interagir com o CRM
def dsa_openai_agent_node(state: AgentState):

    print("\n--- Executando Nó Agente OpenAI (CRM) ---")
    
    try:

        # Inicializa o LLM OpenAI com temperatura baixa e chave de API
        llm_openai = ChatOpenAI(temperature=0.2, openai_api_key=openai_api_key, model_name="gpt-3.5-turbo")
        
        # Define o prompt do sistema com instruções para usar a ferramenta CRM
        system_prompt = """Você é um assistente de CRM experiente chamado OpenAI (modelo GPT).
        Seu objetivo é ajudar o usuário com informações do banco de dados CRM.
        Utilize a ferramenta 'dsa_query_crm_database' para executar consultas SQL SELECT e buscar dados sobre clientes ou interações.
        Refira-se à descrição da ferramenta para entender o schema do banco (tabelas: tb_dsa_clientes, tb_dsa_interacoes; colunas relevantes como name, email, status, interaction_date, type, notes).
        Formule consultas SQL SELECT precisas com base na pergunta do usuário.
        Apresente os resultados de forma clara. Se encontrar um erro da ferramenta, comunique-o.
        Se a informação não estiver disponível, indique isso claramente.
        """
        
        # Cria um agente executável a partir do LLM e do prompt do sistema
        agent_runnable = dsa_cria_agente_runnable(llm_openai, system_prompt)
        
        # Informa que o agente OpenAI foi criado e será invocado
        print("Runnable OpenAI (CRM) criado. Invocando...")
        
        # Invoca o agente com o histórico de mensagens contido no estado
        response = agent_runnable.invoke({"messages": state['messages']})
        
        # Exibe informações sobre o tipo de resposta e parte do seu conteúdo
        print(f"Nó OpenAI (CRM) Obteve Resposta: Tipo={type(response)}, Conteúdo='{response.content[:50]}...'")
        
        # Verifica se a resposta inclui chamadas de ferramentas
        if hasattr(response, 'tool_calls') and response.tool_calls:
            
            # Exibe quais ferramentas foram acionadas pelo agente
            print(f"Nó OpenAI (CRM) está chamando a ferramenta: {response.tool_calls}")
        
        # Retorna o dicionário contendo as mensagens de resposta do agente
        return {"messages": [response]}

    except Exception as e:
        
        # Em caso de exceção, exibe mensagem de erro no console
        print(f"!!! ERRO NO NÓ OpenAI (CRM): {e} !!!")
        
        # Mostra o erro ao usuário na interface Streamlit
        st.error(f"Ocorreu um erro ao contactar a API OpenAI: {e}")
        
        # Cria uma mensagem de erro interna para ser retornada pelo nó
        error_msg = AIMessage(content=f"[ERRO INTERNO OPENAI]: Não foi possível processar com OpenAI. Detalhe: {e}", name="ErroOpenAI")
        
        # Retorna o dicionário contendo a mensagem de erro
        return {"messages": [error_msg]}

# Função para o nó de roteamento
# A lógica de roteamento estará na próxima função
# Mesmo que ela não tenha lógica de processamento, ela atua como nó explícito de roteamento, deixando claro no grafo onde ocorre a decisão central
# Em grafos de fluxo de agentes, é uma boa prática ter nós explícitos que atuam como hubs ou roteadores, mesmo que não modifiquem o estado
def dsa_route_junction_node(state: AgentState) -> dict:
    print("--- Nó de Junção de Roteamento (Sem Mudança de Estado) ---")
    return {}

# Define a função responsável por decidir para onde o roteador deve enviar a próxima mensagem
def dsa_router_logic(state: AgentState) -> str:

    print("\n--- Função Lógica de Roteamento (Decidindo Próximo Passo) ---")

    # Recupera a lista de mensagens do estado atual
    messages = state['messages']
    
    # Seleciona a última mensagem, se existir
    last_message = messages[-1] if messages else None

    # Se não houver nenhuma mensagem, encerra o roteamento
    if not last_message:
        print("Decisão Lógica: Sem mensagens no estado, terminando.")
        return "__end__"

    # Mostra no console informações sobre a última mensagem analisada
    print(f"Roteador analisando última mensagem: Tipo={type(last_message).__name__}, Conteúdo='{last_message.content[:80]}...'")

    # Se a última mensagem for de IA e contiver chamadas de ferramenta, roteia para "tools"
    if isinstance(last_message, AIMessage) and hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        print("Decisão Lógica: Última mensagem AI tem 'tool_calls'. Roteando para Ferramentas.")
        return "tools"

    # Se a última mensagem for de IA sem chamadas de ferramenta, encerra o ciclo atual
    if isinstance(last_message, AIMessage):
        print("Decisão Lógica: Resposta final da IA recebida (sem tool_calls). Terminando o ciclo atual.")
        return "__end__"

    # Se a última mensagem for humana, verifica menções explícitas a roteadores
    if isinstance(last_message, HumanMessage):
        
        # Converte o conteúdo da mensagem para minúsculas para facilitar a comparação
        user_input_current = last_message.content.lower()

        print(f"Analisando última mensagem humana para menções: '{user_input_current}'")
        
        # Roteia para OpenAI se houver menção a "@openai"
        if "@openai" in user_input_current:
            print("Decisão Lógica: Roteando para OpenAI (menção explícita na última mensagem)")
            return "openai_agent"
        
        # Roteia para Groq se houver menção a "@groq"
        elif "@groq" in user_input_current:
            print("Decisão Lógica: Roteando para Groq (menção explícita na última mensagem)")
            return "groq_agent"

    # Se a última mensagem for resultado de ferramenta, indica roteamento alternado
    if isinstance(last_message, ToolMessage):
        print("Decisão Lógica: Resultado da ferramenta recebido, roteando para um agente (via alternância)...")

    # Conta quantas mensagens de IA já foram trocadas para alternar o roteamento
    ai_message_count = sum(1 for msg in messages if isinstance(msg, AIMessage))
    
    print(f"Contagem atual de mensagens AI para alternância: {ai_message_count}")

    # Se o número de respostas de IA for par, roteia para Groq como padrão alternado
    if ai_message_count % 2 == 0:
        print(f"Decisão Lógica: Roteando para Groq (padrão/alternado)")
        return "groq_agent"
    
    # Caso contrário, roteia para OpenAI
    else:
        print(f"Decisão Lógica: Roteando para OpenAI (padrão/alternado)")
        return "openai_agent"

# Define a função responsável por compilar o grafo de estados e transições do agente
def dsa_compila_grafo():

    # Cria uma instância de StateGraph usando AgentState como tipo de estado
    workflow = StateGraph(AgentState)

    # Adiciona o nó que executa o agente OpenAI 
    workflow.add_node("openai_agent", dsa_openai_agent_node)

    # Adiciona o nó que executa o agente Groq
    workflow.add_node("groq_agent", dsa_groq_agent_node)
    
    # Adiciona o nó que trata a execução de ferramentas
    workflow.add_node("tools", tool_node)
    
    # Adiciona o nó de junção/roteamento para decidir o próximo passo
    workflow.add_node("router", dsa_route_junction_node)
    
    # Conecta o ponto de entrada START ao nó de roteamento
    workflow.add_edge(START, "router")
    
    # Configura arestas condicionais saindo do roteador baseado na lógica de roteamento
    workflow.add_conditional_edges(
        "router",
        dsa_router_logic,
        {
            "tools": "tools",
            "groq_agent": "groq_agent",
            "openai_agent": "openai_agent",
            "__end__": END
        },
    )
    
    # Conecta a saída do agente OpenAI de volta ao roteador para o próximo ciclo
    workflow.add_edge("openai_agent", "router")

    # Conecta a saída do agente Groq de volta ao roteador para o próximo ciclo
    workflow.add_edge("groq_agent", "router")
    
    # Conecta a saída das ferramentas de volta ao roteador para o próximo ciclo
    workflow.add_edge("tools", "router")
    
    # Compila o workflow em um aplicativo executável
    app = workflow.compile()
    
    # Imprime no console confirmação de sucesso na compilação
    print("Grafo Compilado com Sucesso!")
    
    # Retorna o aplicativo resultante do grafo compilado
    return app

##### Interface de Deploy com Streamlit #####

# Verifica se o aplicativo ainda não foi inicializado na sessão
if "app" not in st.session_state:

    # Se o arquivo do banco de dados não existir, exibe erro e orienta a criação
    if not os.path.exists(DB_FILE):
        st.error(f"Erro: O arquivo do banco de dados '{DB_FILE}' não foi encontrado.")
        st.info("Por favor, execute o script 'create_crm_db.py' no mesmo diretório para criar o banco de dados e depois recarregue esta página.")
        st.stop()

    # Informa que o grafo será inicializado pela primeira vez
    st.write("Inicializando o grafo pela primeira vez...")

    try:
        
        # Compila o grafo e armazena na sessão
        st.session_state.app = dsa_compila_grafo()
        
        # Define um identificador de thread para controle interno
        st.session_state.thread_id = "streamlit_thread_crm"
        
        # Se o histórico de chat não existir na sessão, inicializa com uma mensagem de boas-vindas
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [
                AIMessage(content="Olá! Sou seu assistente de CRM. Pergunte-me sobre clientes ou interações (ex: 'Quais clientes estão ativos?', 'Mostre as interações de João Silva').")
            ]
        
        # Exibe mensagem de sucesso após inicializar o grafo
        st.success("Grafo CRM inicializado.")
    
    except Exception as e:
        
        # Em caso de erro crítico na construção do grafo, exibe mensagem de erro e a exceção
        st.error(f"Erro crítico ao construir o grafo CRM: {e}")
        st.exception(e)
        
        # Interrompe a execução da aplicação após o erro
        st.stop()

# Sidebar
st.sidebar.title("Memória")

# Expande a seção lateral para exibir o histórico completo da conversa
with st.sidebar.expander("📜 Ver Histórico Completo da Conversa", expanded=False):
    
    # Se houver mensagens no histórico de chat na sessão
    if st.session_state.chat_history:
        
        # Itera sobre cada mensagem armazenada no histórico
        for i, msg in enumerate(st.session_state.chat_history):
            
            # Determina o papel da mensagem (IA, ferramenta ou usuário)
            role = "ai" if isinstance(msg, AIMessage) else ("tool" if isinstance(msg, ToolMessage) else "user")
            
            # Inicializa o nome exibido do remetente como 'Usuário'
            sender_display = "Usuário"
            
            # Se a mensagem for da IA, ajusta o remetente conforme regras de alternância e menções explícitas
            if role == "ai":
                
                # Conta quantas mensagens de IA ocorreram antes desta
                ai_message_index = sum(1 for m in st.session_state.chat_history[:i] if isinstance(m, AIMessage))
                
                # Verifica se há menção explícita ao roteador Groq
                is_groq_explicit = "@groq" in msg.content.lower()
                
                # Verifica se há menção explícita ao roteador OpenAI
                is_openai_explicit = "@openai" in msg.content.lower()
                
                # Obtém o nome personalizado da mensagem, se existir
                msg_name = getattr(msg, 'name', None)
                
                # Define a exibição do remetente seguindo condições de menções e alternância
                if is_groq_explicit or (not is_openai_explicit and ai_message_index % 2 == 0 and not msg_name):
                    sender_display = "AI (Groq/Llama3)"
                elif is_openai_explicit or (not is_groq_explicit and ai_message_index % 2 != 0 and not msg_name):
                    sender_display = "AI (OpenAI/GPT)"
                elif msg_name:
                    sender_display = f"AI ({msg_name})"
                else:
                    sender_display = "AI (Assistente)"
            
            # Se a mensagem for de ferramenta, ajusta o nome do remetente para 'Ferramenta'
            elif role == "tool":
                
                # Obtém o nome da ferramenta ou usa o padrão
                tool_name = getattr(msg, 'name', 'dsa_query_crm_database')
                sender_display = f"Ferramenta ({tool_name})"
            
            # Renderiza o cabeçalho do remetente
            st.markdown(f"**{sender_display}:**")
            
            # Exibe o conteúdo da mensagem em um campo de texto somente leitura
            st.text_area(label=f"msg_{i}", value=msg.content, height=100, disabled=True, label_visibility="collapsed")
            
            # Se a mensagem for de IA e conter chamadas de ferramenta, exibe em formato JSON
            if isinstance(msg, AIMessage) and getattr(msg, 'tool_calls', None):
                st.write("*Chamada(s) de Ferramenta:*")
                st.json([{'name': tc.get('name', 'N/A'), 'args': tc.get('args', {})} for tc in msg.tool_calls])
            
            # Se a mensagem for de ferramenta e tiver ID de chamada, exibe a legenda com o ID
            if isinstance(msg, ToolMessage) and hasattr(msg, 'tool_call_id'):
                st.caption(f"ID da Chamada: {msg.tool_call_id}")
            
            # Adiciona um divisor entre mensagens
            st.divider()
    
    # Se não houver mensagens no histórico, exibe mensagem informativa
    else:
        st.write("Nenhuma mensagem no histórico ainda.")

# Exibe título "Chat Ativo" no corpo principal do Streamlit
st.markdown("### Chat Ativo")

# Cria um container para a área do chat com altura fixa de 500 pixels
container_chat = st.container(height = 500)

# Inicia o contexto para renderizar dentro do container do chat
with container_chat:

    # Itera sobre o histórico de mensagens armazenado na sessão
    for i, msg in enumerate(st.session_state.chat_history):
        
        # Determina o papel da mensagem: 'ai', 'tool' ou 'user'
        role = "ai" if isinstance(msg, AIMessage) else ("tool" if isinstance(msg, ToolMessage) else "user")
        
        # Define ícone padrão de avatar para usuário
        avatar_icon = "👤"
        
        # Define nome padrão do remetente como "Usuário"
        sender_name = "Usuário"
        
        # Define papel padrão para o componente de chat do Streamlit
        message_role_for_streamlit = "user"

        # Se a mensagem for da IA, ajusta ícone, nome e papel
        if role == "ai":
            
            # Define papel de mensagem para o assistente no componente de chat
            message_role_for_streamlit = "assistant"
            
            # Conta quantas mensagens de IA já ocorreram antes desta
            ai_message_index = sum(1 for m in st.session_state.chat_history[:i] if isinstance(m, AIMessage))
            
            # Verifica menção explícita a "@groq" no conteúdo da mensagem
            is_groq_explicit = "@groq" in msg.content.lower()
            
            # Verifica menção explícita a "@openai" no conteúdo da mensagem
            is_openai_explicit = "@openai" in msg.content.lower()
            
            # Obtém nome específico da mensagem caso exista
            msg_name = getattr(msg, 'name', None)
            
            # Se for Groq ou alternância com índice par e sem nome, define avatar Groq
            if is_groq_explicit or (not is_openai_explicit and ai_message_index % 2 == 0 and not msg_name):
                 avatar_icon = "🦙"
                 sender_name = "Groq (Llama3)"
            
            # Se for OpenAI ou alternância com índice ímpar e sem nome, define avatar OpenAI
            elif is_openai_explicit or (not is_groq_explicit and ai_message_index % 2 != 0 and not msg_name):
                 avatar_icon = "🤔"
                 sender_name = "OpenAI (GPT)"
            
            # Se existir nome personalizado na mensagem, usa avatar de sistema
            elif msg_name:
                 avatar_icon = "⚠️"
                 sender_name = f"Sistema ({msg_name})"
            
            # Caso contrário, usa avatar genérico de assistente
            else:
                 avatar_icon = "🤖"
                 sender_name = "Assistente"
        
        # Se a mensagem for de ferramenta, ajusta papel, avatar e nome
        elif role == "tool":
             
             # Define papel de mensagem para o assistente no componente de chat
             message_role_for_streamlit = "assistant"
             
             # Define ícone de ferramenta
             avatar_icon = "🛠️"
             
             # Define nome do remetente como "Ferramenta"
             sender_name = "Ferramenta"

        # Renderiza cada mensagem no componente de chat com avatar e papel definidos
        with st.chat_message(message_role_for_streamlit, avatar=avatar_icon):
            
            # Se a mensagem for de ferramenta, exibe resultado com formatação
            if role == "tool":
                
                # Obtém nome da ferramenta ou usa valor padrão
                tool_name = getattr(msg, 'name', 'dsa_query_crm_database')
                
                # Exibe título do resultado da ferramenta
                st.markdown(f"**Resultado Ferramenta ({tool_name})**:")
                
                # Exibe conteúdo da ferramenta em bloco de código
                st.code(f"{msg.content}", language=None)
                
                # Exibe legenda com o ID da chamada da ferramenta
                st.caption(f"ID Chamada: {msg.tool_call_id}")
            
            # Se a mensagem for da IA, exibe conteúdo e chamadas de ferramenta se houver
            elif role == "ai":
                
                # Exibe nome do remetente da IA em negrito
                st.markdown(f"**{sender_name}:**")
                
                # Se existirem chamadas de ferramenta, exibe em formato JSON
                if getattr(msg, 'tool_calls', None):
                     st.write(f"*Chamando ferramenta(s):*")
                     st.json([{'name': tc.get('name', 'N/A'), 'args': tc.get('args', {})} for tc in msg.tool_calls])
                
                # Exibe o conteúdo da mensagem da IA
                st.markdown(msg.content)
            
            # Se for mensagem do usuário, exibe diretamente o texto
            else:
                
                # Exibe o conteúdo da mensagem do usuário
                st.markdown(msg.content)

# Se o usuário inserir uma pergunta no chat
if prompt := st.chat_input("Faça uma pergunta sobre o CRM..."):
    
    # Adiciona a mensagem humana ao histórico de chat na sessão
    st.session_state.chat_history.append(HumanMessage(content=prompt))
    
    # Reinicia a execução da aplicação para processar a entrada
    st.rerun()

# Gerenciamento da Memória e Inicialização do Estado Para os Agentes de IA
# Se existir histórico de chat e a última mensagem for do usuário
if st.session_state.chat_history and isinstance(st.session_state.chat_history[-1], HumanMessage):
    
    # Armazena a última mensagem humana
    last_human_message = st.session_state.chat_history[-1]
    
    # Se ainda não estivermos processando outra requisição
    if not st.session_state.get("processing_lock", False):
        
        # Ativa o bloqueio de processamento
        st.session_state["processing_lock"] = True
        
        # Prepara o estado atual com todas as mensagens
        current_state = {"messages": st.session_state.chat_history}
        
        # Exibe um spinner indicando consulta ao CRM e pensamento do agente
        with st.spinner("Consultando CRM e pensando..."):
            
            # Inicializa a variável de retorno do grafo
            final_state = None

            try:
                
                # Invoca o grafo a partir do estado atual
                final_state = st.session_state.app.invoke(current_state)
                
                # Se o grafo retornou um estado válido contendo mensagens
                if final_state and "messages" in final_state:
                    
                    # Extrai apenas as novas mensagens geradas após a invocação
                    new_messages = final_state["messages"][len(current_state["messages"]):]
                    
                    # Se houver novas mensagens, adiciona ao histórico
                    if new_messages:
                        st.session_state.chat_history.extend(new_messages)
                    else:
                        # Informa que não houve novas mensagens nesta rodada
                        st.toast("O grafo não retornou novas mensagens desta vez.", icon="🤔")
                else:
                    
                    # Informa que o estado retornado foi inválido
                    st.toast("O grafo retornou um estado inválido.", icon="error")
                    
                    # Registra mensagem de erro interno no histórico
                    st.session_state.chat_history.append(AIMessage(content="Desculpe, ocorreu um erro interno no estado do grafo."))
            
            except Exception as e:
                
                # Exibe o erro ocorrido durante a execução do grafo
                st.error(f"Erro durante a execução do grafo: {e}")
                
                # Adiciona mensagem de erro ao histórico de chat
                st.session_state.chat_history.append(AIMessage(content=f"Desculpe, ocorreu um erro: {e}"))
            
            finally:
                
                # Libera o bloqueio de processamento
                st.session_state["processing_lock"] = False
                
                # Reinicia a aplicação para atualizar a interface com novos dados
                st.rerun()

# Título da barra lateral do Streamlit
st.sidebar.divider()
st.sidebar.title("Instruções")

# Exibe instruções para o usuário na barra lateral
st.sidebar.markdown("""
Digite sua pergunta ao lado para conversar com os Agentes de IA.

Os Agentes são capazes de consultar o banco de dados de CRM para extrair as respostas.

Tipos de perguntas:
- **Quais clientes estão ativos?**
- **Qual interação foi feita com João Silva?**
- **Cite o nome de um dos clientes listados anteriormente.**
- **Quais clientes tiveram interação por e-mail?**
- **Algum cliente foi lead capturado com interação via formulário do site?**
- **Quais interações ocorreram em 29-04-2025?**

IA Generativa comete erros. **SEMPRE** use seu conhecimento para verificar as respostas.
""")

# Botão de suporte na barra lateral que exibe mensagem ao clicar
if st.sidebar.button("Suporte"):
    st.sidebar.write("Dúvidas? Envie um e-mail para: suporte@datascienceacademy.com.br")



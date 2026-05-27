# Projeto 7 - Gerenciamento de Memória e Contexto - Sistema de Multi-Agentes de IA com LangGraph Para Automação do CRM e Consulta a Banco de Dados
# Módulo de Criação do Banco de Dados

# Imports
import os
import sqlite3
from datetime import datetime, timedelta

# Define o nome do arquivo de banco de dados SQLite
DB_FILE = "dsa_crm_database.db"

# Declara a função responsável por criar e conectar ao banco de dados SQLite
def dsa_cria_database():

    # Inicializa a variável de conexão como None
    conn = None

    # Início do bloco de tratamento de exceções para operações de banco de dados
    try:

        # Conecta-se ao arquivo de banco de dados SQLite ou cria se não existir
        conn = sqlite3.connect(DB_FILE)
        
        # Cria um cursor para executar comandos SQL
        cursor = conn.cursor()

        # Exibe mensagem de conexão bem-sucedida
        print(f"Conectado ao banco de dados: {DB_FILE}")

        # Executa comando SQL para criar a tabela de clientes se ela não existir
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tb_dsa_clientes (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            company TEXT,
            status TEXT CHECK(status IN ('Lead', 'Active', 'Inactive', 'Prospect')) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Informa que a tabela de clientes foi criada/verificada
        print("Tabela 'tb_dsa_clientes' verificada/criada.")

        # Executa comando SQL para criar a tabela de interações se ela não existir
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tb_dsa_interacoes (
            interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            interaction_date TIMESTAMP NOT NULL,
            type TEXT CHECK(type IN ('Email', 'Call', 'Meeting', 'Note')) NOT NULL,
            notes TEXT,
            FOREIGN KEY (customer_id) REFERENCES tb_dsa_clientes (customer_id)
        )
        """)

        # Informa que a tabela de interações foi criada/verificada
        print("Tabela 'tb_dsa_interacoes' verificada/criada.")

        # Aplica as alterações no banco de dados
        conn.commit()

        # Informa que a estrutura do banco está pronta
        print("Estrutura do banco de dados pronta.")

        # Retorna a conexão e o cursor para uso posterior
        return conn, cursor

    # Captura possíveis erros de SQLite e exibe mensagem de erro
    except sqlite3.Error as e:

        print(f"Erro ao criar/conectar ao banco de dados: {e}")

        # Se a conexão foi aberta, fecha para evitar vazamento de recursos
        if conn:
            conn.close()

        # Retorna None para indicar falha na criação/conexão
        return None, None

# Declara a função que popula as tabelas com dados de exemplo
def dsa_popula_tabelas(conn, cursor):

    # Informa início do processo de inserção de dados de exemplo
    print("Populando com dados de exemplo...")

    # Bloco de tratamento de erros para inserção de dados
    try:

        # Define lista de tuplas com dados de clientes de exemplo
        tb_dsa_clientes_data = [
            ('João Silva', 'joao.silva@email.com', '11-9999-0001', 'Empresa Alpha', 'Active'),
            ('Maria Oliveira', 'maria.o@sample.net', '21-8888-0002', 'Serviços Beta', 'Active'),
            ('Pedro Souza', 'pedro.souza@example.org', '31-7777-0003', 'Consultoria Gama', 'Lead'),
            ('Ana Costa', 'ana.costa@email.com', '41-6666-0004', 'Empresa Alpha', 'Inactive'),
            ('Carlos Lima', 'carlos.lima@sample.net', '51-5555-0005', 'Tec Delta', 'Prospect')
        ]

        # Inicializa contador de clientes inseridos
        inserted_tb_dsa_clientes = 0

        # Itera sobre cada cliente na lista de dados de exemplo
        for customer in tb_dsa_clientes_data:

            try:

                # Executa inserção de registro de cliente na tabela
                cursor.execute("""
                INSERT INTO tb_dsa_clientes (name, email, phone, company, status)
                VALUES (?, ?, ?, ?, ?)
                """, customer)
                
                # Incrementa contador para cada inserção bem-sucedida
                inserted_tb_dsa_clientes += 1

            # Trata violação de chave única para evitar duplicatas
            except sqlite3.IntegrityError:

                # Informa que o cliente já existe e ignora a inserção
                print(f"Cliente com email {customer[1]} já existe. Ignorando.")

        # Exibe quantos clientes foram inseridos
        print(f"{inserted_tb_dsa_clientes} novos clientes inseridos.")

        # Recupera IDs de clientes e seus emails para mapeamento
        cursor.execute("SELECT customer_id, email FROM tb_dsa_clientes")

        # Cria dicionário mapeando email para customer_id
        customer_map = {email: cid for cid, email in cursor.fetchall()}

        # Define data atual para uso em interações
        today = datetime.now()

        # Lista de tuplas com interações de exemplo usando o mapeamento de IDs
        tb_dsa_interacoes_data = [
            (customer_map.get('joao.silva@email.com'), (today - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'), 'Call', 'Primeira ligação, mostrou interesse.'),
            (customer_map.get('joao.silva@email.com'), (today - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'), 'Email', 'Enviou proposta comercial.'),
            (customer_map.get('maria.o@sample.net'), (today - timedelta(days=20)).strftime('%Y-%m-%d %H:%M:%S'), 'Meeting', 'Reunião inicial de apresentação.'),
            (customer_map.get('maria.o@sample.net'), (today - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'), 'Email', 'Follow-up pós reunião.'),
            (customer_map.get('pedro.souza@example.org'), (today - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'), 'Note', 'Lead capturado via formulário do site.'),
            (customer_map.get('carlos.lima@sample.net'), (today - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'), 'Email', 'Contato inicial enviado.')
        ]

        # Filtra apenas interações com IDs de clientes válidos
        valid_tb_dsa_interacoes = [inter for inter in tb_dsa_interacoes_data if inter[0] is not None]

        # Se existirem interações válidas, executa inserção em lote
        if valid_tb_dsa_interacoes:

            cursor.executemany("""
            INSERT INTO tb_dsa_interacoes (customer_id, interaction_date, type, notes)
            VALUES (?, ?, ?, ?)
            """, valid_tb_dsa_interacoes)

            # Informa quantas interações foram inseridas
            print(f"{len(valid_tb_dsa_interacoes)} interações inseridas.")
        else:
            # Informa ausência de interações válidas para inserção
            print("Nenhuma interação válida para inserir (verifique se os clientes foram inseridos).")

        # Confirma as operações de inserção no banco
        conn.commit()

        # Mensagem final de sucesso na inserção de dados de exemplo
        print("Dados de exemplo inseridos com sucesso.")

    # Captura erros de SQLite durante a inserção e efetua rollback
    except sqlite3.Error as e:
        print(f"Erro ao inserir dados de exemplo: {e}")
        conn.rollback()

# Função principal do script, executa criação e população do banco
def main():

    # Verifica se o arquivo de banco já existe
    if os.path.exists(DB_FILE):
        print(f"Banco de dados '{DB_FILE}' já existe.")

    # Chama a função para criar/conectar ao banco de dados e obtém conexão e cursor
    conn, cursor = dsa_cria_database()

    # Se a conexão e o cursor foram obtidos com sucesso, popula as tabelas
    if conn and cursor:

        # Executa a função
        dsa_popula_tabelas(conn, cursor)

        # Fecha a conexão após a população das tabelas
        conn.close()

        # Mensagem informando que a conexão foi fechada
        print("Conexão com o banco de dados fechada.")

# Verifica se o script está sendo executado diretamente
if __name__ == "__main__":

    print("\nIniciando a criação do banco de dados de CRM.\n")

    main()

    print("\nBanco de dados criado com sucesso.\n")



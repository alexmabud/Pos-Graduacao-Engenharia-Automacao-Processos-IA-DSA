# Projeto 2 - Construção de Multi-Agentes de IA com CrewAI e Deploy via API com Docker

# Imports
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool

print('\nIniciando o Trabalho do Time de Agentes Jurídicos Baseados em IA Generativa!\n')

# Carrega o arquivo de variáveis de ambiente
load_dotenv(override=True)

# Verifica se a variável de ambiente da API foi carregada
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Nenhuma chave de API encontrada nas variáveis de ambiente")

print('\nAPI Para os LLMs dos Agentes Carregada com Sucesso!\n')

# Inicializa a ferramenta de busca genérica
search_tool = Tool(name = "DuckDuckGo Search",
                   func = lambda query: DuckDuckGoSearchRun().run(query),
                   description = "Executa buscas na web usando o DuckDuckGo")

# Inicializa a ferramenta de busca na Wikipedia
wikipedia_tool = Tool(name = "Wikipedia Search",
                      func = lambda query: WikipediaQueryRun(api_wrapper = WikipediaAPIWrapper()).run(query),
                      description = "Busca informações na Wikipedia")

# Inicializa os LLMs (agentes) específicos de função

# Define o LLM do Agente Pesquisador
pesquisador_llm = ChatOpenAI(api_key = api_key,
                             model = "gpt-4o",
                             temperature = 0.7)

# Define o LLM do Agente Assistente Jurídico
assistente_juridico_llm = ChatOpenAI(api_key = api_key,
                                     model = "gpt-4o",
                                     temperature = 0.2)

# Define o LLM do Agente Criador de Relatórios
criador_relatorio_llm = ChatOpenAI(api_key = api_key,
                                   model = "gpt-4o",
                                   temperature = 0.5)

# Cria o Agente Pesquisador
pesquisador = Agent(
    role='Analista de Pesquisa Sênior',
    goal='Realizar pesquisas completas e reunir dados relevantes',
    backstory="""Você é um analista de pesquisa sênior com 15 anos de experiência em análise de dados
    e pesquisa de mercado. Você tem Pós-Graduação em Ciência de Dados pela Data Science Acacdemy e é 
    especialista em reconhecimento de padrões e análise de tendências. Você se destaca em:
    1. Encontrar e validar informações de várias fontes
    2. Identificar tendências e padrões emergentes
    3. Avaliação crítica da qualidade e relevância dos dados
    4. Fornecer contexto e insights para tópicos complexos""",
    verbose=True,
    tools=[search_tool, wikipedia_tool],  
    allow_delegation=True,
    llm=pesquisador_llm 
)

# Cria o Agente Assistente Jurídico
assistente_juridico = Agent(
    role='Assistente Jurídico',
    goal='Processar e transformar dados em formatos úteis',
    backstory="""Você é um assistente jurídico sênior com experiência na área de Direito, 
    especializado nos padrões jurídicos do Brasil. Suas especialidades incluem:
    1- Preparar e organizar documentos legais, como contratos e petições
    2- Realizar pesquisas jurídicas para apoiar advogados em casos específicos
    3- Acompanhar prazos processuais e gerenciar o calendário de atividades do escritório
    4- Redigir pareceres jurídicos sob supervisão de advogados
    Você sempre garante a integridade dos dados ao prepará-los para análise.""",
    verbose=True,
    allow_delegation=True,
    llm=assistente_juridico_llm 
)

# Cria o Agente Criador de Relatórios
criador_relatorio = Agent(
    role='Criador de Relatórios',
    goal='Criar relatórios abrangentes e detalhados',
    backstory="""Você é um especialista em construção de relatórios e redator técnico
    com um olhar atento aos detalhes. Seus pontos fortes incluem:
    1. Criar relatórios objetivos, claros e impactantes
    2. Traduzir dados complexos em insights compreensíveis
    3. Estruturar informações para máxima clareza
    4. Manter consistência nos padrões de relatórios
    Você se destaca em tornar informações complexas acessíveis a todas as partes interessadas.""",
    verbose=True,
    allow_delegation=True,
    llm=criador_relatorio_llm 
)

# Função para executar o time de agentes
def dsa_execute_time_agentes(topic):
    try:
        # Cria a lista de tarefas para o tópico
        tasks = [
            Task(
                description=f"""Pesquise sobre {topic} de forma detalhada. 
                Reúna dados e informações relevantes de fontes confiáveis.
                Forneça um resumo das principais descobertas.""",
                agent=pesquisador,
                expected_output="Um resumo estruturado com as principais descobertas sobre o tópico pesquisado."
            ),
            Task(
                description=f"""Limpe e processe os dados coletados sobre {topic}.
                Identifique e trate quaisquer valores ausentes ou anomalias, se existirem.
                Prepare os dados para análise e criação de relatório.""",
                agent=assistente_juridico,
                expected_output="Dados processados e organizados, prontos para a geração do relatório final."
            ),
            Task(
                description=f"""Crie um relatório abrangente sobre {topic} usando os dados processados.
                Inclua insights relevantes.
                Garanta que o relatório seja claro e acionável.""",
                agent=criador_relatorio,
                expected_output="Um relatório detalhado e bem estruturado, contendo insights relevantes sobre o tema."
            )
        ]

        # Cria o Time de Agentes (Crew)
        time_juridico = Crew(agents=[pesquisador, assistente_juridico, criador_relatorio],
                             tasks=tasks,
                             verbose=True)

        print("\nIniciando execução do time de agentes...\n")

        # Inicializa o time de agentes e salva o resultado
        result = time_juridico.kickoff()

        print("\nExecução concluída!\n")
        return result

    except Exception as e:
        return f"Ocorreu um erro: {str(e)}"


# Bloco de execução
if __name__ == "__main__":

    # Define o tópico
    topico = "Jurisprudência de prisão em segunda instância no Brasil"

    print('\nTópico Definido. O Time de Agentes Entrará em Ação!\n')

    # Extrai o resultado
    resultado = dsa_execute_time_agentes(topico)

    # Imprime
    print("\nResultado:", resultado)

    print('\nObrigado Por Usar o Time de Agentes Jurídicos Baseados em IA Generativa da Data Science Academy!\n')



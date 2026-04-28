# 🎓 Caderno Técnico — Pós-Graduação

Documento técnico consolidado dos 8 projetos do Módulo 2 (Inteligência Aumentada com RAG, GraphRAG e Agentic RAG — Data Science Academy). Todas as informações foram extraídas diretamente do código-fonte (`*.py`, `*.ipynb`, `requirements.txt`, `Dockerfile`, `docker-compose.yaml`, `LEIAME.txt`).

---

## Índice

- [Visão Geral](#visão-geral)
- [Projeto 1 — LLMOps com LLM, RAG, Airflow, ElasticSearch e Grafana](#projeto-1--llmops-com-llm-rag-airflow-elasticsearch-e-grafana)
- [Projeto 2 — SQL + LLM + RAG via API (FastAPI) para Recomendação Personalizada](#projeto-2--sql--llm--rag-via-api-fastapi-para-recomendação-personalizada)
- [Projeto 3 — SLM (TinyLlama) + RAG com Qdrant para Triagem Médica](#projeto-3--slm-tinyllama--rag-com-qdrant-para-triagem-médica)
- [Projeto 4 — SLM + RAG + Engenharia de Prompt para Assistente de RH](#projeto-4--slm--rag--engenharia-de-prompt-para-assistente-de-rh)
- [Projeto 5 — GraphRAG (Grafo de Conhecimento) para Análise de Contratos](#projeto-5--graphrag-grafo-de-conhecimento-para-análise-de-contratos)
- [Projeto 6 — Agentic RAG com LangGraph para Análise de Contratos](#projeto-6--agentic-rag-com-langgraph-para-análise-de-contratos)
- [Projeto 7 — Agentic RAG + LLM Routing para Suporte Técnico](#projeto-7--agentic-rag--llm-routing-para-suporte-técnico)
- [Projeto 8 — Agentic RAG Multimodal (Gemini Vision) para Análise Contábil](#projeto-8--agentic-rag-multimodal-gemini-vision-para-análise-contábil)
- [📚 Glossário Técnico](#-glossário-técnico)
- [🗺️ Mapa de Tecnologias](#️-mapa-de-tecnologias)
- [🧭 Guia de Decisão Rápida](#-guia-de-decisão-rápida)

---

## Visão Geral

A pós-graduação trabalha **IA Generativa aplicada a problemas reais**, com foco em **Retrieval-Augmented Generation (RAG)** em suas variantes mais modernas. A trilha vai do RAG clássico ao Agentic RAG multimodal, passando por LLMOps de produção.

**Temas cobertos**:
- LLMOps: empacotamento via Docker, orquestração via Airflow, observabilidade via Grafana.
- RAG clássico: ElasticSearch (BM25) e bancos vetoriais (Qdrant, FAISS).
- Engenharia de prompt: few-shot, role prompting, condensação de pergunta.
- SLMs (Small Language Models) executados localmente: TinyLlama, Gemma3 via Ollama.
- LLMs em nuvem via API: OpenAI (GPT-4o, GPT-4o-mini, text-embedding-3-small), Groq (Llama 3.1/3.3), Google Gemini (Flash Vision), HuggingFace (BERT-large SQuAD).
- GraphRAG: grafos de conhecimento com NetworkX + similaridade cosseno + conceitos compartilhados.
- Agentic RAG: workflows compostos com LangGraph (`StateGraph`), incluindo roteadores de LLM e fluxos multimodais.
- Frontends de IA: Streamlit (predominante), Gradio, FastAPI + cliente Python.

**Stack base recorrente**: Python 3.12, LangChain (`langchain`, `langchain-community`, `langchain-core`), LangGraph, FAISS, HuggingFaceEmbeddings, Streamlit, Conda para isolamento de ambientes (cada projeto define `dsaragpN`).

**Progressão didática observada**:
1. Projeto 1 ensina LLMOps de ponta a ponta (RAG textual + métricas).
2. Projetos 2–4 introduzem RAG em diferentes frontends (API, notebook, Streamlit) com SLMs e LLMs distintos.
3. Projeto 5 muda de paradigma: RAG baseado em grafo, não em similaridade vetorial pura.
4. Projetos 6–7 introduzem Agentic RAG via LangGraph, com complexidade crescente (3 nós → roteador + busca web).
5. Projeto 8 fecha com agente multimodal (texto + imagem) para domínio contábil.

---

## Projeto 1 — LLMOps com LLM, RAG, Airflow, ElasticSearch e Grafana

📁 [projetos_1_modulo_2/](projetos_1_modulo_2/)

### 📌 Objetivo
Aplicação de IA generativa para Q&A sobre documentos jurídicos em inglês, com **pipeline completo de produção**: ingestão automatizada via Airflow, indexação em ElasticSearch (RAG), inferência via LLM hospedado na HuggingFace, persistência de avaliação em PostgreSQL e dashboard de monitoramento em Grafana. Tudo orquestrado com Docker Compose.

### 🧰 Tecnologias Utilizadas

#### Docker / Docker Compose
- **O que é**: Plataforma de containerização e orquestração local multi-container.
- **Por que foi usada aqui**: O `docker-compose.yaml` define **8 serviços interdependentes** (postgres, redis, airflow-webserver, airflow-scheduler, airflow-triggerer, airflow-init, elasticsearch, app, grafana). Sem Compose seria inviável subir esse stack de forma reproduzível.
- **Prós**: Subida com um comando (`docker-compose -p dsap1 up --build -d`); rede `bridge` isola os serviços; volumes nomeados (`postgres-db-volume`, `elastic-search-data`, `grafana-storage`) garantem persistência.
- **Contras**: Cold start lento; troubleshooting de hostnames internos é confuso (o LEIAME alerta que é preciso editar o hostname do ElasticSearch manualmente).
- **Quando usar**: POCs e ambientes locais de desenvolvimento que combinam vários serviços.
- **Quando NÃO usar**: Produção real (use Kubernetes/ECS); apps single-binary.

#### Apache Airflow 2.10.4
- **O que é**: Orquestrador de workflows como DAGs Python.
- **Por que foi usada aqui**: Carrega o RAG em 4 etapas sequenciais — `tarefa_cria_tabela >> tarefa_carrega_json >> tarefa_carrega_csv >> tarefa_cria_indice`. A DAG `DSA_Carrega_Dados_RAG` roda diariamente (`schedule_interval="0 0 * * *"`).
- **Prós**: UI clara (`localhost:8080`); retries automáticos (`retries=1`, `retry_delay=timedelta(hours=1)`); separação limpa entre orquestração e código.
- **Contras**: Pesado para tarefas simples (precisa Postgres + Redis + Scheduler + Webserver); curva de aprendizado de operadores.
- **Quando usar**: Pipelines de dados recorrentes com dependências.
- **Quando NÃO usar**: Tarefas one-shot ou baseadas em eventos (use cron, Prefect ou EventBridge).

#### ElasticSearch 8.15.1
- **O que é**: Motor de busca de texto distribuído baseado em Lucene.
- **Por que foi usada aqui**: Implementa o RAG **léxico** (não vetorial). Em [dsaelasticSearch.py:20-39](projetos_1_modulo_2/dsamoduloapp/streamlit/app/dsaelasticSearch.py#L20-L39), usa `multi_match` com boost no campo `question` (peso 2) e `text` (peso 1), tipo `best_fields`, retornando os 5 melhores documentos.
- **Prós**: Excelente para keyword search e BM25; sem custo de embeddings; rápido em escala.
- **Contras**: Não captura semântica (sinônimos, paráfrases); RAM-hungry; mapeamentos rígidos.
- **Quando usar**: Quando o usuário busca por termos exatos (jargão jurídico, códigos).
- **Quando NÃO usar**: Busca por similaridade conceitual — use Qdrant/FAISS/Pinecone.

#### PostgreSQL 13
- **O que é**: Banco relacional usado tanto pelo Airflow (metadados) quanto pela aplicação (avaliação/feedback).
- **Por que foi usada aqui**: Três tabelas — `dsa_documentos` (corpus para RAG), `dsa_avaliacao` (métricas por consulta) e `dsa_feedback` (satisfação do usuário). Veja `dsa_captura_user_input` em [dsallm.py:55-108](projetos_1_modulo_2/dsamoduloapp/streamlit/app/dsallm.py#L55-L108).
- **Prós**: ACID, maduro, integra nativamente com Airflow e Grafana.
- **Contras**: Reuso do mesmo banco do Airflow para dados de aplicação é decisão didática — em prod isso seria separado.
- **Quando usar**: Dados estruturados, transações, auditoria.

#### HuggingFace Inference API (BERT-large SQuAD)
- **O que é**: API de inferência hospedada para modelos do HuggingFace.
- **Por que foi usada aqui**: O LLM `google-bert/bert-large-uncased-whole-word-masking-finetuned-squad` é um modelo extractive QA (não generativo). Recebe `question` + `context` e retorna span da resposta + `score`. Veja [dsallm.py:30-52](projetos_1_modulo_2/dsamoduloapp/streamlit/app/dsallm.py#L30-L52).
- **Prós**: Sem custo de hospedagem do modelo; latência aceitável para POCs.
- **Contras**: Cold start em modelos free; rate limits; **modelo extractive não gera texto novo** (só recorta o contexto).
- **Quando usar**: QA factual sobre documentos onde a resposta literal está no texto.
- **Quando NÃO usar**: Quando a resposta requer síntese ou raciocínio — use modelo generativo.

#### Streamlit 1.39.0
- **O que é**: Framework Python para construir UIs interativas.
- **Por que foi usada aqui**: Interface web do assistente em `localhost:8501`, com input, botão, exibição de resposta e botões de feedback (Satisfeito/Não Satisfeito) gravados no Postgres.
- **Prós**: Zero CSS/JS para fluir; `st.session_state` resolve estado.
- **Contras**: Re-renderiza tudo a cada interação; multi-usuário simultâneo é frágil.

#### Grafana
- **O que é**: Plataforma de dashboards e observabilidade.
- **Por que foi usada aqui**: Conecta no Postgres e plota métricas das tabelas `dsa_avaliacao` e `dsa_feedback` (hit_rate, MRR, response_time, taxa de satisfação).
- **Prós**: Dashboards versionáveis (existe `dsadashboardgrafana/dashboard.json`); alertas; muitos data sources.
- **Contras**: Configuração inicial de datasource manual (LEIAME pede ajuste pós-deploy).

#### Métricas de Avaliação (hit_rate, MRR)
- **O que é**: `hit_rate` = fração de queries onde algum documento relevante apareceu no top-k. `MRR` (Mean Reciprocal Rank) = média de `1/(posição do primeiro relevante)`.
- **Por que foi usada aqui**: Implementadas em [dsaevaluation.py](projetos_1_modulo_2/dsamoduloapp/streamlit/app/dsaevaluation.py). Comparam o `doc_id` retornado contra um ground truth em CSV (`dadosHistoricos/dataset.csv`).

### 🏗️ Arquitetura / Fluxo

```
┌─────────────────┐  DAG diária  ┌──────────────┐   indexa   ┌────────────────┐
│ dataset1.jsonl  │─────────────▶│   Airflow    │───────────▶│ ElasticSearch  │
│ dataset2.csv    │ (4 tarefas)  │ (PythonOps)  │            │   "dsaindex"   │
└─────────────────┘              └──────┬───────┘            └────────┬───────┘
                                        │                             │
                                        ▼                             │
                                ┌──────────────┐                      │
                                │ PostgreSQL   │                      │
                                │ dsa_documentos│                     │
                                └──────────────┘                      │
                                                                      │
        Usuário ──pergunta──▶ ┌──────────────────┐ ──multi_match─────▶┘
                              │ Streamlit (8501) │
                              │   appdsa.py      │ ──contexto+question──▶ HuggingFace BERT
                              └──────┬───────────┘                              │
                                     │ insere                                   │
                                     ▼                                          │
                              ┌──────────────┐                                  │
                              │ PostgreSQL   │◀─────────────resposta────────────┘
                              │ dsa_avaliacao│
                              │ dsa_feedback │
                              └──────┬───────┘
                                     │
                                     ▼
                              ┌──────────────┐
                              │   Grafana    │
                              │   (3000)     │
                              └──────────────┘
```

### 💡 Conceitos-Chave Aprendidos
- **LLMOps**: ciclo de vida de uma aplicação de LLM em produção (ingestão, inferência, observabilidade, feedback loop).
- **RAG léxico vs. semântico**: este projeto usa BM25 puro (ElasticSearch), não embeddings.
- **Doc ID determinístico**: `dsa_gera_id_documento` usa MD5 truncado em 8 chars. Útil para idempotência de ingestão e correlação com ground truth.
- **Avaliação online**: cada consulta dispara `evaluate(...)` que recalcula hit_rate/MRR contra ground truth — útil para monitorar drift.

### ⚠️ Pontos de Atenção
- **SQL injection**: `dsa_captura_user_input` usa f-string para montar SQL com input do usuário (`'{userQuery}'`). É vulnerável; o `replace("'", "")` antes mitiga parcialmente, mas em produção use parâmetros (`%s`) como já é feito em `dsa_insere_dados_json`.
- **Bug em `dsa_cria_indice`** ([dsa_carrega_dados.py:184-225](projetos_1_modulo_2/dsamoduloairflow/dags/modulodsadados/dsa_carrega_dados.py#L184-L225)): `indexName` é referenciado antes de ser definido (linha 204 vs. 212). Provavelmente o índice nunca é criado com mappings — só os documentos são indexados com mapping dinâmico.
- **Hostname hardcoded**: `Elasticsearch("http://elasticsearch:9200")` depende do nome do serviço Compose; o LEIAME avisa que pode ser preciso editar manualmente.
- **Dataset truncado**: ingere apenas os primeiros 25 registros de cada arquivo (`dsaDados[0:25]`, `head(25)`) — é didático.

### 🔗 Conexão com outros projetos
- Único projeto que usa **Airflow + Docker Compose + ElasticSearch + Grafana**.
- Usa **HuggingFace API** (modelo extractive); demais projetos usam OpenAI, Groq, Google Gemini ou Ollama (modelos generativos).
- Streamlit aparece também nos projetos 4, 5, 6, 7 e 8.
- PostgreSQL aparece **só aqui**; demais projetos usam SQLite (P2) ou nenhum DB relacional.

---

## Projeto 2 — SQL + LLM + RAG via API (FastAPI) para Recomendação Personalizada

📁 [projetos_2_modulo_2/](projetos_2_modulo_2/)

### 📌 Objetivo
API REST que cadastra dados de pacientes em um SQLite e, em endpoint separado, monta um prompt com os dados do paciente e pede ao GPT-4o **recomendações de tratamento médico** personalizadas. Demonstra **RAG estruturado** (banco SQL como base de conhecimento) atrás de uma API.

### 🧰 Tecnologias Utilizadas

#### FastAPI 0.115.8
- **O que é**: Framework web Python assíncrono baseado em Starlette + Pydantic.
- **Por que foi usada aqui**: Define dois endpoints — `POST /dsa_cadastra_paciente` e `GET /dsa_llm_recomenda_tratamento/`. Usa `@asynccontextmanager` em `lifespan` para criar a tabela `dsa_tb_dados_pacientes` na inicialização ([app.py:52-60](projetos_2_modulo_2/app.py#L52-L60)).
- **Prós**: Tipagem com Pydantic gera validação automática; doc OpenAPI gratuita em `/docs`; rápido.
- **Contras**: Erros de pydantic podem ser verbosos; dependency injection tem curva de aprendizado.
- **Quando usar**: APIs Python modernas com tipagem forte.
- **Quando NÃO usar**: Apps full-stack com SSR pesado (use Django).

#### Gunicorn + Uvicorn
- **O que é**: Gunicorn é process manager WSGI/ASGI; Uvicorn é servidor ASGI para FastAPI.
- **Por que foi usada aqui**: O LEIAME instrui `gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app` — 4 workers asyncio para paralelismo real.
- **Prós**: Paralelismo entre processos contorna o GIL; reload de workers automático.
- **Contras**: Em Windows o Gunicorn não roda nativamente.

#### SQLite 3 (`sqlite3` builtin)
- **O que é**: Banco relacional embutido em arquivo único.
- **Por que foi usada aqui**: O arquivo `dsa_db_p2.db` é criado/aberto a cada conexão. Tabela `dsa_tb_dados_pacientes(id, nome_paciente, idade, genero, sintomas)`. Note `conn.row_factory = sqlite3.Row` para acesso por nome de coluna.
- **Prós**: Zero setup; arquivo único portável.
- **Contras**: Concorrência limitada (lock no arquivo); não escala horizontalmente.

#### OpenAI Python SDK 1.63.2 (modelo `gpt-4o`)
- **O que é**: SDK oficial; aqui usa Chat Completions com `model="gpt-4o"`.
- **Por que foi usada aqui**: Em [app.py:141-149](projetos_2_modulo_2/app.py#L141-L149), monta um system prompt ("Você é um especialista médico...") + user prompt com `Sintomas/idade/genero` do paciente e pede recomendações em até 150 tokens.
- **Prós**: Qualidade alta; SDK ergonômico.
- **Contras**: Pago; latência variável; sujeito a rate limits da OpenAI.

#### python-dotenv
- Carrega `.env` com `OPENAI_API_KEY`. Note o **fallback gracioso** em [app.py:62-68](projetos_2_modulo_2/app.py#L62-L68): se a chave não estiver configurada, o cadastro continua funcionando, só a recomendação retorna 503.

### 🏗️ Arquitetura / Fluxo

```
Cliente 1 (CLI)              Cliente 2 (CLI)
dsa_api_cliente_1.py         dsa_api_cliente_2.py
       │                              │
       │ POST cadastra                │ GET recomenda
       ▼                              ▼
┌─────────────────────────────────────────────┐
│            FastAPI (app.py)                 │
│  ┌──────────────┐    ┌────────────────────┐ │
│  │ /dsa_cadastra│    │/dsa_llm_recomenda  │ │
│  │   _paciente  │    │   _tratamento/     │ │
│  └──────┬───────┘    └────────┬───────────┘ │
│         │                     │             │
│         ▼                     ▼             │
│  ┌──────────────┐    ┌────────────────────┐ │
│  │   SQLite     │───▶│ Monta prompt com   │ │
│  │ pacientes    │    │ dados + chama LLM  │ │
│  └──────────────┘    └────────┬───────────┘ │
│                               │             │
└───────────────────────────────┼─────────────┘
                                ▼
                         ┌─────────────┐
                         │ OpenAI GPT-4o│
                         └─────────────┘
```

### 💡 Conceitos-Chave Aprendidos
- **RAG estruturado**: o "retrieval" é um `SELECT` SQL, não busca vetorial. Quando os dados já são bem estruturados, não há por que vetorizar.
- **API-first**: separar ingestão (cliente 1) de inferência (cliente 2) é padrão para sistemas multi-cliente.
- **Lifespan handlers**: forma moderna FastAPI para inicialização (substitui o antigo `@app.on_event("startup")`).
- **UPDATE concatenando** ([app.py:99](projetos_2_modulo_2/app.py#L99)): `SET sintomas = sintomas || ', ' || ?` acumula sintomas em re-cadastros.

### ⚠️ Pontos de Atenção
- **Chave da OpenAI**: o código tolera ausência da chave (continua sem o LLM); é um padrão útil para POCs.
- **Match case-insensitive** com `LOWER(TRIM(nome_paciente))` evita falhas por digitação.
- **Sem autenticação**: API totalmente aberta — só serve para POC local.

### 🔗 Conexão com outros projetos
- **OpenAI** aparece também no Projeto 5 (`gpt-4o-mini` + `text-embedding-3-small`).
- Único projeto que usa **FastAPI**; demais usam Streamlit ou Gradio.
- Único projeto sem RAG vetorial — RAG aqui é puro SQL.

---

## Projeto 3 — SLM (TinyLlama) + RAG com Qdrant para Triagem Médica

📁 [projetos_3_modulo_2/](projetos_3_modulo_2/)

### 📌 Objetivo
Aplicação de **automação de processo médico de triagem** que combina busca semântica em base de Q&A médico (16.407 perguntas/respostas no `dataset.csv`) com **SLM local (TinyLlama-1.1B)** para gerar respostas de até 3-4 pontos. Interface Gradio.

### 🧰 Tecnologias Utilizadas

#### Sentence Transformers (`sentence-transformers/all-mpnet-base-v2`)
- **O que é**: Biblioteca para gerar embeddings densos de sentenças via modelos baseados em BERT.
- **Por que foi usada aqui**: Modelo `all-mpnet-base-v2` (768 dim) gera vetores das 100 perguntas iniciais; `model.encode(question)` é chamado em runtime para vetorizar a query do usuário.
- **Prós**: Modelo top-tier público; suporta GPU; embeddings de alta qualidade.
- **Contras**: 768 dim é pesado para coleções grandes; latência sem GPU é alta.
- **Quando usar**: RAG semântico em qualquer idioma com bom suporte multilíngue.
- **Quando NÃO usar**: Quando precisa de modelo specialized (legal, biomedical) — use BioMPNet, Legal-BERT.

#### Qdrant (modo `:memory:`)
- **O que é**: Banco vetorial em Rust com cliente Python; suporta in-memory ou servidor.
- **Por que foi usada aqui**: Em [Projeto3.ipynb cell 19](projetos_3_modulo_2/Projeto3.ipynb), `QdrantClient(":memory:")` cria coleção `doc_data` com `Distance.COSINE` e dimensão = `len(vetores[0])`.
- **Prós**: API limpa; suporta filtros + busca híbrida; modo in-memory perfeito para POC.
- **Contras**: In-memory perde dados ao reiniciar; quotas de memória sob alta carga.
- **Quando usar**: Vector DBs production-grade com self-host.
- **Quando NÃO usar**: Necessidade de SQL+vetorial unificado — use pgvector.

#### TinyLlama-1.1B-Chat-v1.0 (transformers + CUDA)
- **O que é**: Small Language Model com 1.1B parâmetros, fine-tunado para chat.
- **Por que foi usada aqui**: Carregado via `AutoModelForCausalLM.from_pretrained(nome_llm, device_map="cuda")` no notebook (Colab com GPU). Geração com `do_sample=True`, `max_new_tokens=500`, `temperature=1.5` (criativo).
- **Prós**: Cabe em GPU pequena (~2GB); livre; rápido.
- **Contras**: Qualidade limitada vs GPT-4; segue mal instruções complexas; a `temperature=1.5` é alta — produz output errático.
- **Quando usar**: POCs com restrição de custo/privacidade.
- **Quando NÃO usar**: Tarefas críticas com baixa tolerância a erro.

#### Gradio 5.19.0
- **O que é**: Framework UI Python orientado a ML.
- **Por que foi usada aqui**: `gr.Interface(fn, inputs, outputs)` cria UI em 10 linhas; `webapp.launch(share=True)` gera URL pública por 72h (útil para Colab).
- **Prós**: Compartilhamento via tunnel automático; integração com HuggingFace Spaces.
- **Contras**: Customização visual limitada; menos componentes que Streamlit.
- **Quando usar**: Demos rápidas de modelos ML.

#### `set_seed(1234)` e `TOKENIZERS_PARALLELISM=True`
- Reprodutibilidade da geração; paralelização da tokenização.

#### `os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"`
- Workaround para conflito entre versões de protobuf C++ e Python (comum no Colab com TF + transformers).

### 🏗️ Arquitetura / Fluxo

```
dataset.csv (16.407 Q&A médicos, 100 primeiros usados)
       │
       ▼
all-mpnet-base-v2 ──encode──▶ vetores (768 dim)
       │
       ▼
QdrantClient(":memory:")  →  Coleção "doc_data" (Distance.COSINE)
       │
Pergunta do usuário (Gradio)
       ▼
encode(pergunta) → query_points → top_1 ID → answer_data[id] = contexto
       │
       ▼
TinyLlama-1.1B-Chat (device="cuda")
       │ chat template + system role "medical clinic assistant"
       ▼
Resposta em 3-4 pontos
```

### 💡 Conceitos-Chave Aprendidos
- **Distância cosseno**: por que é a métrica padrão para embeddings textuais (independente do tamanho do vetor).
- **Pipeline RAG mínimo**: encode → store → retrieve → augment-prompt → generate.
- **Chat templates** via `tokenizer.apply_chat_template`: formato específico de cada modelo (TinyLlama segue Zephyr-style).
- **`add_generation_prompt=True`**: insere o token de turno do assistente para forçar geração.

### ⚠️ Pontos de Atenção
- **`device_map="cuda"` hardcoded**: o código quebra em máquinas sem GPU. O notebook tem comentário avisando para trocar por `"cpu"` (mas a `to("cuda")` em outra linha também precisa).
- **Erro pré-existente** mostrado no notebook: `'MessageFactory' object has no attribute 'GetPrototype'` (conflito protobuf — daí o workaround acima).
- **Carrega modelo de embedding 2x**: `dsa_recupera_dados` chama `SentenceTransformer(...)` a cada query (linhas 4-6 da função). Em produção, instancie uma vez globalmente.
- **Apenas 100 registros**: `[:100]` para velocidade em Colab; com volume real, use `iter_documents` + batch encode.

### 🔗 Conexão com outros projetos
- **Sentence Transformers** aparece nos Projetos 1 (não), 4 (`all-MiniLM-L6-v2` via langchain-huggingface), 6 (`all-mpnet-base-v2` via langchain-huggingface).
- Único projeto que usa **Qdrant** e **TinyLlama**; demais usam FAISS + LLMs em nuvem ou Ollama.
- Único projeto que roda em **notebook Colab com GPU**.
- Único projeto com **Gradio**.

---

## Projeto 4 — SLM + RAG + Engenharia de Prompt para Assistente de RH

📁 [projetos_4_modulo_2/](projetos_4_modulo_2/)

### 📌 Objetivo
Streamlit chat para análise de currículos `.docx` (3 candidatos: financeiro, logística, qualidade). O usuário pergunta sobre os candidatos; o sistema usa RAG sobre os currículos e um SLM **local via Ollama (gemma3:4b)** para gerar respostas em PT-BR.

### 🧰 Tecnologias Utilizadas

#### LlamaIndex 0.12.24 (`SimpleDirectoryReader`, `VectorStoreIndex`)
- **O que é**: Framework concorrente do LangChain, focado em RAG.
- **Por que foi usada aqui**: `SimpleDirectoryReader(input_dir="./documentos", recursive=True)` lê os `.docx`; `VectorStoreIndex.from_documents(docs)` cria o índice vetorial usando os globals em `Settings.llm` e `Settings.embed_model`.
- **Prós**: Abstração mais alta-nível que LangChain; ótima integração com Ollama; `index.as_chat_engine(chat_mode="condense_question")` faz o "engineering de prompt" sozinho.
- **Contras**: Comunidade menor que LangChain; abstrações às vezes ocultam o que está rodando.
- **Quando usar**: RAG canônico onde você não quer customizar muito.
- **Quando NÃO usar**: Workflows agentic complexos — use LangGraph.

#### Ollama (`gemma3:4b`) via `llama-index-llms-ollama`
- **O que é**: Runtime local para LLMs open-source (estilo Docker para modelos).
- **Por que foi usada aqui**: `Ollama(model="gemma3:4b", request_timeout=600.0)`. Gemma 3 4B é o LLM da Google rodando 100% local — sem custo, sem internet.
- **Prós**: Privacidade absoluta; sem chave API; suporta vários modelos; excelente para dados sensíveis (currículos têm PII).
- **Contras**: Performance dependente do hardware local; modelos 4B são limitados; precisa instalar e baixar o modelo (`ollama pull gemma3:4b`).
- **Quando usar**: Dados sensíveis, ambientes air-gapped, dev offline.
- **Quando NÃO usar**: Apps que exigem qualidade GPT-4.

#### HuggingFaceEmbeddings (`sentence-transformers/all-MiniLM-L6-v2`)
- **O que é**: Wrapper LangChain para embeddings HuggingFace.
- **Por que foi usada aqui**: 384 dim, modelo leve, ideal para 3 documentos. Chamado via `langchain_huggingface.HuggingFaceEmbeddings`.
- **Prós**: 5x mais leve que `all-mpnet-base-v2`; rápido.
- **Contras**: Qualidade ligeiramente inferior em buscas multilíngues longas.

#### docx2txt 0.8
- **O que é**: Lib para extrair texto puro de `.docx`.
- **Por que foi usada aqui**: Importado mas, na prática, o `SimpleDirectoryReader` do LlamaIndex já cobre `.docx` via `python-docx` (também listado em requirements). O import é redundante mas não causa erro.

#### Streamlit `@st.cache_resource(show_spinner=False)`
- Cacheia o índice criado por `dsa_modulo_rag()` para não reindexar a cada interação. Crucial dado que indexar 3 currículos com Ollama leva 1-2 minutos.

#### `chat_mode="condense_question"`
- **Engenharia de prompt embutida**: dada a pergunta atual + histórico, o LlamaIndex pede ao LLM para reformular numa pergunta autocontida antes de buscar no RAG. Resolve referências anafóricas ("e o segundo candidato?").

### 🏗️ Arquitetura / Fluxo

```
documentos/
├── curriculo_analista_financeiro.docx
├── curriculo_analista_logistica.docx
└── curriculo_analista_qualidade.docx
       │
       ▼ (SimpleDirectoryReader recursive)
   docs (lista de Document)
       │
       ▼
   Settings.embed_model = HF all-MiniLM-L6-v2
   Settings.llm         = Ollama gemma3:4b
       │
       ▼
   VectorStoreIndex.from_documents(docs)  ──cache──▶ @st.cache_resource
       │
       ▼
   index.as_chat_engine(chat_mode="condense_question", verbose=True)
       │
   Pergunta usuário ──▶ contextual_prompt ("Você é assistente RH...PT-BR")
       │                          │
       │                          ▼
       └──▶ chat_engine.chat(prompt) ──▶ resposta no Streamlit
                                          │
                                          ▼
                              session_state.messages (histórico)
```

### 💡 Conceitos-Chave Aprendidos
- **`VectorStoreIndex`**: índice vetorial em memória do LlamaIndex (default usa `SimpleVectorStore`).
- **`condense_question`**: padrão Conversational RAG — funde histórico com pergunta atual.
- **Globals via `Settings`**: LlamaIndex usa singleton de configuração (`Settings.llm`, `Settings.embed_model`) — diferente do LangChain que injeta tudo.
- **Engenharia de prompt contextual** ([dsaprojeto4.py:111-112](projetos_4_modulo_2/dsaprojeto4.py#L111-L112)): o prompt fixa role ("assistente de RH"), explicita a tarefa e força o idioma.

### ⚠️ Pontos de Atenção
- **Dependência externa do Ollama**: o usuário precisa ter Ollama instalado + rodando + com `gemma3:4b` baixado, senão o app trava em `request_timeout=600`.
- **Cache de recurso e mudança de docs**: se você adicionar um novo currículo, é preciso limpar o cache do Streamlit (botão clear cache ou rerun manual).
- **Sem persistência do índice**: a cada cold start, reindexa tudo. Para acelerar, salve com `index.storage_context.persist(persist_dir=...)`.

### 🔗 Conexão com outros projetos
- **HuggingFaceEmbeddings** aparece também no Projeto 6 (`all-mpnet-base-v2`).
- **Streamlit chat** com `st.chat_input` e `st.chat_message` aparece só aqui (demais usam `text_input`).
- **LlamaIndex** aparece só aqui; demais usam LangChain.
- **Ollama** aparece só aqui; demais usam APIs cloud (OpenAI, Groq, Gemini, HuggingFace).

---

## Projeto 5 — GraphRAG (Grafo de Conhecimento) para Análise de Contratos

📁 [projetos_5_modulo_2/](projetos_5_modulo_2/)

### 📌 Objetivo
Análise de contratos PDF combinando RAG vetorial (FAISS) com **grafo de conhecimento** construído sobre os chunks do documento. A traversal usa fila de prioridade (Dijkstra-like) e verifica iterativamente se o contexto acumulado já responde à pergunta antes de continuar a expansão.

### 🧰 Tecnologias Utilizadas

#### FAISS-CPU 1.10.0 (`IndexFlatL2`)
- **O que é**: Lib do Facebook AI para busca por similaridade em alta dimensão.
- **Por que foi usada aqui**: Em [dsa_processa_documentos.py:91-95](projetos_5_modulo_2/graphrag/dsa_processa_documentos.py#L91-L95), `IndexFlatL2(dimension)` cria índice exato (sem aproximação) com distância L2.
- **Prós**: Ultra-rápido; sem servidor; simples.
- **Contras**: `IndexFlatL2` é exato e não escala para milhões de vetores (use `IndexIVFPQ`).
- **Quando usar**: Vector store local, em memória, até centenas de milhares de docs.

#### NetworkX 3.4.2
- **O que é**: Lib Python para grafos.
- **Por que foi usada aqui**: `nx.Graph()` em [dsa_knowledgegraph.py:64](projetos_5_modulo_2/graphrag/dsa_knowledgegraph.py#L64). Cada chunk vira um nó; arestas são adicionadas quando a similaridade cosseno entre embeddings > 0.8 (`edges_threshold`). O peso da aresta é `0.7 * similarity + 0.3 * normalized_shared_concepts`.
- **Prós**: API ergonômica; algoritmos prontos (BFS, Dijkstra).
- **Contras**: Em grafos enormes (milhões de nós), `igraph` é mais rápido.

#### OpenAI (`text-embedding-3-small` + `gpt-4o-mini`)
- Embeddings: 1536 dim, modelo mais novo e barato que `ada-002`.
- LLM: `gpt-4o-mini` para extração de conceitos, verificação de contexto e resposta final ([dsa_processa_documentos.py:44-54](projetos_5_modulo_2/graphrag/dsa_processa_documentos.py#L44-L54)).
- A chave é lida de `st.secrets["API_KEY"]` (`.streamlit/secrets.toml`).

#### NLTK + WordNet
- **Por que foi usada aqui**: `WordNetLemmatizer` em [dsa_knowledgegraph.py:246-247](projetos_5_modulo_2/graphrag/dsa_knowledgegraph.py#L246-L247) normaliza conceitos (ex: "running" → "run") antes de comparar — evita criar arestas duplicadas para variações morfológicas.

#### `RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)`
- Padrão LangChain: tenta separar por `\n\n`, depois `\n`, depois `.`, mantendo coesão semântica.

#### `streamlit-chat`
- Componente externo que renderiza balões de conversa com avatares (`fun-emoji`, `bottts`).

#### `ThreadPoolExecutor`
- Usado em (a) carregamento concorrente do PDF + (b) extração paralela de conceitos por chunk em [dsa_knowledgegraph.py:179-197](projetos_5_modulo_2/graphrag/dsa_knowledgegraph.py#L179-L197).

### 🏗️ Arquitetura / Fluxo

```
Contrato PDF
    │
    ▼ PyPDFLoader (limita 20 páginas)
  documents
    │
    ▼ RecursiveCharacterTextSplitter(1000, 200)
  splits (chunks)
    │
    ├─────────────▶ OpenAI text-embedding-3-small ─▶ FAISS IndexFlatL2
    │
    └─────────────▶ knowledgeGraph.build_graph(splits):
                      1. _add_nodes  (cada chunk = nó)
                      2. _extract_concepts (paralelo, gpt-4o-mini extrai conceitos+entidades)
                      3. _create_embeddings → cosine_similarity
                      4. _add_edges (sim > 0.8 ⇒ aresta com peso 0.7·sim + 0.3·shared_concepts)

Query do usuário
    │
    ▼ QueryEngine.query(query)
    │
    ├─▶ _retrieve_relevant_documents (FAISS top-5)
    │
    ▼ _expand_context (Dijkstra-like com heapq):
        1. Para cada doc relevante: empurra na priority queue (priority = 1/sim)
        2. Pop nó de menor priority → adiciona conteúdo ao contexto expandido
        3. AnswerCheck.check_answer(query, contexto): "Sim/Não, contexto é completo?"
        4. Se sim → break. Se não → expande para vizinhos no grafo (distance += 1/edge_weight)
        5. Lematiza conceitos visitados para evitar revisitar
    │
    ▼
  Final answer (gpt-4o-mini, temperature=0.3)
```

### 💡 Conceitos-Chave Aprendidos
- **GraphRAG**: superar limitações do top-k clássico ao seguir relações semânticas no grafo (chunks "vizinhos" via conceitos compartilhados).
- **Iterative answer checking**: o LLM julga se o contexto já é suficiente — economiza tokens e expansão desnecessária.
- **Edge weighting híbrido** (similaridade + conceitos): pondera estrutura semântica do texto, não só o vetor.
- **Lematização para deduplicação**: aplicar em runtime evita explosão combinatória de conceitos.

### ⚠️ Pontos de Atenção
- **Custo**: `_extract_concepts` faz 2 chamadas ao GPT por chunk (entidades + conceitos). Para um doc com 50 chunks, são 100 chamadas só na ingestão.
- **`AnswerCheck.check_answer`**: o prompt mistura "Sim/Não" em PT com `"Yes" in text_response`. O `"Yes"` em string é instável (pode vir "Sim" e o código devolver `is_complete=False` sempre). É um bug sutil em [dsa_queryengine.py:39](projetos_5_modulo_2/graphrag/dsa_queryengine.py#L39).
- **Chave API**: lida de `st.secrets["API_KEY"]` — depende do `.streamlit/secrets.toml` estar configurado corretamente.
- **PDF limitado a 20 páginas**: `documents[:20]` em [dsaprojeto5.py:25](projetos_5_modulo_2/dsaprojeto5.py#L25) — para POC, não para prod.
- **`OpenAIEmbedding.embed_documents`** recebe **uma string**, não uma lista (o nome do método é enganador). Veja loop em [dsa_processa_documentos.py:81-83](projetos_5_modulo_2/graphrag/dsa_processa_documentos.py#L81-L83).

### 🔗 Conexão com outros projetos
- **FAISS** aparece também nos Projetos 6, 7, 8.
- **OpenAI** aparece também no Projeto 2.
- **PyPDFLoader** aparece também no Projeto 6.
- **`RecursiveCharacterTextSplitter`** aparece nos Projetos 6, 7, 8.
- Único projeto com **GraphRAG via NetworkX**.

---

## Projeto 6 — Agentic RAG com LangGraph para Análise de Contratos

📁 [projetos_6_modulo_2/](projetos_6_modulo_2/)

### 📌 Objetivo
CLI Python que analisa contratos PDF usando **Agentic RAG** baseado em LangGraph com 3 nós sequenciais. Resposta gerada pelo Llama 3.3 70B via Groq, embeddings locais via HuggingFace, índice FAISS persistido em disco.

### 🧰 Tecnologias Utilizadas

#### LangGraph 0.3.25 (`StateGraph`)
- **O que é**: Lib da LangChain para construir grafos de estado para agentes.
- **Por que foi usada aqui**: Em [dsaprojeto6.py:280-289](projetos_6_modulo_2/dsaprojeto6.py#L280-L289), define `AgentState` (TypedDict com `question/documents/context/answer`), 3 nós e arestas lineares: `retrieve → format_context → generate → END`.
- **Prós**: Estado centralizado e tipado; visualização do fluxo; fácil estender com `add_conditional_edges`.
- **Contras**: Para fluxos lineares simples, é overkill (uma `RunnableSequence` faria igual).
- **Quando usar**: Workflows com decisões condicionais, retries, ciclos.
- **Quando NÃO usar**: Pipelines puramente lineares.

#### Groq (`llama-3.3-70b-versatile`) via `langchain-groq` 0.3.2
- **O que é**: Plataforma de inferência LLM com hardware especializado (LPU); oferece Llama 3 com latência abaixo de 1s.
- **Por que foi usada aqui**: `ChatGroq(api_key, model_name="llama-3.3-70b-versatile", temperature=0)` — `temperature=0` para respostas determinísticas em domínio jurídico.
- **Prós**: Velocidade absurda (>500 tok/s); free tier generoso; modelos open-source.
- **Contras**: Rate limits agressivos no free tier; menos modelos que OpenAI.
- **Quando usar**: Aplicações que precisam de latência baixa com Llama/Mixtral.

#### HuggingFaceEmbeddings (`sentence-transformers/all-mpnet-base-v2`)
- 768 dim, mesmo modelo do Projeto 3 mas via wrapper LangChain.

#### FAISS persistente (`save_local` / `load_local`)
- **Padrão importante**: em [dsaprojeto6.py:136-160](projetos_6_modulo_2/dsaprojeto6.py#L136-L160), se `dsavectordb/` existe, **carrega** com `FAISS.load_local(..., allow_dangerous_deserialization=True)`; senão cria do zero. Isso evita reindexar a cada execução.
- `allow_dangerous_deserialization=True` é necessário porque FAISS usa `pickle` (que pode executar código arbitrário). Aceitável em arquivos próprios.

#### `ChatPromptTemplate` + `StrOutputParser` + `RunnablePassthrough`
- Pipeline funcional ao estilo LCEL (LangChain Expression Language) em [dsaprojeto6.py:259-264](projetos_6_modulo_2/dsaprojeto6.py#L259-L264).

#### `python-dotenv`
- Carrega `GROQ_API_KEY` do `.env`. Falha rápido se não definida.

#### `RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)`
- Chunks maiores que no P5 — adequado para contratos com cláusulas longas.

#### `retriever = vector_store.as_retriever(search_kwargs={'k': 5})`
- Top-5 chunks por consulta.

### 🏗️ Arquitetura / Fluxo

```
documentos/Contrato.pdf
    │
    ▼ PyPDFLoader + RecursiveCharacterTextSplitter(1500, 200)
  fragments (com metadata source, page)
    │
    ▼ HuggingFaceEmbeddings(all-mpnet-base-v2)
    ▼ FAISS.from_documents → save_local("dsavectordb")
    │ (skip se já existir)
    ▼
LangGraph StateGraph(AgentState):

  ┌──────────────────┐
  │ START            │
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐    state["question"]
  │ retrieve         │    retriever.invoke(question, k=5)
  │ (recupera_       │ ─▶ state["documents"] = [Doc, Doc, ...]
  │  documentos)     │
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐    state["documents"]
  │ format_context   │    formata "Fonte: X (Página: Y)\n\nconteudo"
  │ (formata_        │ ─▶ state["context"] = string
  │  contexto)       │
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐    LCEL chain:
  │ generate         │    {context, question} | rag_prompt | ChatGroq | StrOutputParser
  │ (gera_resposta)  │ ─▶ state["answer"] = string
  └────────┬─────────┘
           │
           ▼
        END
```

Loop CLI lê pergunta, invoca `agent_app.invoke({"question": query})`, imprime resposta + fontes únicas dos documentos recuperados.

### 💡 Conceitos-Chave Aprendidos
- **LangGraph para Agentic RAG**: separar retrieval, formatação e geração em nós distintos facilita observabilidade (cada nó imprime seu progresso) e teste isolado.
- **`TypedDict` como contrato de estado**: não é Pydantic, mas dá tipagem suficiente para o IDE.
- **LCEL** (`prompt | llm | parser`): forma idiomática de compor cadeias no LangChain moderno.
- **Persistência de índice vetorial**: padrão "build once, query many".
- **Engenharia de prompt com fontes**: o prompt instrui "Cite o(s) documento(s) fonte" — exige que metadata flua até o prompt.

### ⚠️ Pontos de Atenção
- **Linhas 49-50** declaram `import os` duas vezes (já importado linha 4). Sem efeito, mas duplicado.
- **`embeddings_model` é instanciado no top-level** — carrega o modelo HF mesmo só para servir queries. Em produção, faça lazy.
- **`vector_store` é referenciado dentro de `dsa_recupera_documentos` mas é definido só no `if __name__`**: funciona porque é variável global atribuída antes do `agent_app.invoke`, mas é frágil — uma execução fora do `__main__` quebra.

### 🔗 Conexão com outros projetos
- **LangGraph** aparece também nos Projetos 7 (com roteador) e 8 (multimodal). Este é a versão "linear" mais simples.
- **FAISS persistido** aparece nos Projetos 7 e 8 (mesmo padrão `save_local`/`load_local`).
- **Groq + Llama** aparece também no Projeto 7.
- **PyPDFLoader** aparece também no Projeto 5; aqui é usado em loop sobre uma pasta.
- Mesmo dataset (`Contrato.pdf`) que Projeto 5 — boa comparação direta GraphRAG vs Agentic RAG.

---

## Projeto 7 — Agentic RAG + LLM Routing para Suporte Técnico

📁 [projetos_7_modulo_2/](projetos_7_modulo_2/)

### 📌 Objetivo
Sistema de suporte técnico onde um **roteador LLM** decide se a pergunta deve ser respondida via RAG (base interna de documentos PDF de suporte) ou via **busca web** (DuckDuckGo). Streamlit UI. Setup do índice é separado em `dsa_p7_setup_rag.py`.

### 🧰 Tecnologias Utilizadas

#### FastEmbed via `langchain-community` (`BAAI/bge-small-en-v1.5`)
- **O que é**: Lib de embeddings da Qdrant otimizada com ONNX runtime; modelo `bge-small-en-v1.5` tem 384 dim e excelente trade-off qualidade/velocidade.
- **Por que foi usada aqui**: Substitui sentence-transformers para reduzir dependências (não precisa torch); ~3-5x mais rápido que sentence-transformers em CPU.
- **Prós**: Sem dependência de PyTorch; ONNX é portátil; embeddings de alta qualidade.
- **Contras**: Menos modelos disponíveis que sentence-transformers.
- **Quando usar**: Produção em CPU, ambientes minimalistas.

#### LangGraph com aresta condicional (`add_conditional_edges`)
- **Padrão chave**: em [dsa_p7_streamlit_app.py:255-259](projetos_7_modulo_2/dsa_p7_streamlit_app.py#L255-L259), o nó `route_query_node` decide via LLM, e a função `dsa_decide_source_edge` lê `state["source_decision"]` para roteá-la para `retrieve_rag_node` OU `search_web_node`.

#### Dois LLMs Groq diferentes para tarefas diferentes
- **Roteador**: `llama-3.1-8b-instant` com `temperature=0.4` (modelo pequeno e rápido — barato para cada decisão).
- **Resposta final**: `llama-3.3-70b-versatile` com `temperature=0.1` (modelo grande para qualidade).
- **Padrão LLM Routing**: usar SLM para tarefas simples (classificação, decisão) e LLM grande só para o output final reduz custo e latência.

#### DuckDuckGoSearchRun (`langchain_community.tools`)
- Faz busca web sem chave API (scrape direto); ferramenta padrão de "agente com acesso à internet" em demos.
- **Prós**: Sem API key; sem custo.
- **Contras**: DuckDuckGo bloqueia agressivamente em alta frequência; resultados crus em texto sem ranqueamento.

#### Few-Shot Prompting no roteador
- O prompt em [dsa_p7_streamlit_app.py:99-113](projetos_7_modulo_2/dsa_p7_streamlit_app.py#L99-L113) inclui **5 exemplos** de query→fonte. Isso é literatura clássica de prompting (Brown et al. 2020 — GPT-3 paper).

#### Fallback robusto
- Em [dsa_p7_streamlit_app.py:135-141](projetos_7_modulo_2/dsa_p7_streamlit_app.py#L135-L141): se o LLM responder algo diferente de "RAG" ou "WEB", o código defaulta para "WEB" (mais seguro — informação atualizada).

#### `@st.cache_resource`
- Aplicado em `dsa_carrega_llm_resposta_final`, `dsa_carrega_retriever` e `dsa_compile_graph` — todos custosos.

### 🏗️ Arquitetura / Fluxo

```
SETUP (dsa_p7_setup_rag.py — roda uma vez):
    dsa_pdfs/*.pdf
        │
        ▼ PyPDFDirectoryLoader(recursive=True) + RecursiveCharacterTextSplitter(1000, 150)
        ▼ FastEmbedEmbeddings(BAAI/bge-small-en-v1.5)
        ▼ FAISS.from_documents().save_local("dsa_faiss_index")

APP (dsa_p7_streamlit_app.py):
    Pergunta do usuário
        │
        ▼
    LangGraph StateGraph(GraphState):
    ┌──────────────────┐
    │ route_query_node │  ChatGroq llama-3.1-8b-instant, temp=0.4
    │  (Few-shot prompt│  → "RAG" | "WEB"
    │   classifica)    │
    └────────┬─────────┘
             │
             │ dsa_decide_source_edge (conditional)
             ├──"RAG"──▶ ┌──────────────────┐
             │           │ retrieve_rag_node│  retriever.invoke(query, k=5)
             │           │                  │  → state["rag_context"]
             │           └────────┬─────────┘
             │                    │
             └──"WEB"──▶ ┌──────────────────┐
                         │ search_web_node  │  DuckDuckGoSearchRun().run(query)
                         │                  │  → state["web_results"]
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │generate_answer   │  ChatGroq llama-3.3-70b, temp=0.1
                         │  _node           │  Prompt: "use APENAS o contexto"
                         └────────┬─────────┘
                                  │
                                  ▼
                                 END
                                  │
                                  ▼
                  st.markdown(answer) + st.info("Fonte: RAG/WEB")
```

### 💡 Conceitos-Chave Aprendidos
- **LLM Routing**: padrão de decompor uma tarefa em "decisão + execução" usando modelos diferentes.
- **Conditional edges no LangGraph**: viabilizam ramificações dinâmicas; a função de decisão recebe o estado e retorna o nome do próximo nó.
- **Few-shot prompting**: 5 exemplos diversos guiam o classificador melhor que descrição abstrata.
- **`Literal[...]` em TypedDict**: tipa enums no estado (`source_decision: Literal["RAG", "WEB", ""]`).
- **Cache de recursos pesados** com `@st.cache_resource`: padrão Streamlit obrigatório para recursos com warm-up alto.

### ⚠️ Pontos de Atenção
- **DuckDuckGo bloqueio**: em uso intenso, retorna 429 ou texto vazio. Para prod, troque por Tavily / SerpAPI / Bing.
- **`temperature=0.4` no roteador**: baixa, mas não zero — pode dar respostas inconsistentes. Para classificação binária, considere `0.0` + `top_p=1`.
- **Decisão default WEB**: significa que se o roteador falhar, vai à internet. Em domínio sensível (médico, jurídico), prefira fail-closed (responder "não sei").
- **Sem ciclo de retry**: se a busca web falhar, retorna mensagem genérica de erro — não tenta o RAG como fallback.
- **`final_answer_raw` é bruto**: ao contrário do P8, este projeto não limpa caracteres invisíveis.

### 🔗 Conexão com outros projetos
- **LangGraph** aparece também nos Projetos 6 (linear) e 8 (multimodal); este é o de complexidade intermediária com decisão.
- **FAISS persistido + FastEmbed** mesma stack do P8.
- **Groq Llama 3.3 70B** mesma do P6, mas aqui combinada com Llama 3.1 8B Instant.
- Padrão `setup_rag.py` separado do `streamlit_app.py` aparece também no P8.

---

## Projeto 8 — Agentic RAG Multimodal (Gemini Vision) para Análise Contábil

📁 [projetos_8_modulo_2/](projetos_8_modulo_2/)

### 📌 Objetivo
Análise multimodal de **notas fiscais (imagens PNG/JPG/JPEG/WEBP)**: o usuário envia a imagem + uma pergunta. O sistema busca contexto em manuais de contabilidade (RAG) e envia tudo (texto + RAG context + imagem em base64) para o **Google Gemini Flash** que retorna análise — incluindo detecção de anomalias.

### 🧰 Tecnologias Utilizadas

#### Google Gemini (`gemini-flash-latest`) via `langchain-google-genai`
- **O que é**: LLM multimodal nativo da Google (`Gemini 1.5/2.0 Flash`).
- **Por que foi usada aqui**: Aceita texto + imagem na mesma mensagem. `temperature=0.2` para consistência analítica.
- **Prós**: Multimodal nativo (vs OpenAI que separa GPT-4o + Vision); barato; janela de contexto grande.
- **Contras**: Inconsistente em rendering de caracteres especiais (daí a função `dsa_clean_llm_output` em [dsa_p8_streamlit_app.py:339-353](projetos_8_modulo_2/dsa_p8_streamlit_app.py#L339-L353)).
- **Quando usar**: Análise de imagens, documentos digitalizados, OCR contextual.
- **Quando NÃO usar**: Quando precisa de imagens em alta resolução com detalhes finos — Gemini comprime.

#### Mensagem multimodal LangChain
- **Padrão fundamental** em [dsa_p8_streamlit_app.py:200-219](projetos_8_modulo_2/dsa_p8_streamlit_app.py#L200-L219): `HumanMessage(content=[{"type": "text", "text": ...}, {"type": "image_url", "image_url": "data:{mime};base64,{b64}"}])`. Esse formato é compatível com Gemini, GPT-4o, Claude.

#### `base64.b64encode(image_bytes).decode('utf-8')`
- Padrão de embed de imagem direto na mensagem (data URL). Alternativa: passar URL pública.

#### Limpeza de output do LLM
- A função `dsa_clean_llm_output` resolve problemas reais observados com Gemini: caracteres `ˊ`, `ˊ`, `\xa0`, `​-‍﻿` (zero-width chars). Reflete experiência de produção: **nunca confie no output cru do LLM para UI**.

#### `<pre>` em `st.markdown`
- Em vez de `st.markdown(answer)` que renderiza Markdown, usa `<pre>...</pre>` para mostrar texto puro com formatação preservada.

#### `st.expander` para debug
- Dois expanders: "Saída crua do LLM" e "Contexto RAG utilizado". Padrão excelente para debugging de aplicações de IA.

#### FastEmbed (`BAAI/bge-small-en-v1.5`) + FAISS persistido
- Mesmo stack do P7 — RAG textual sobre os manuais de contabilidade em PDF.

#### LangGraph linear (2 nós)
- Mais simples que P7: `retrieve_rag_node → analyze_invoice_node → END`. Não há roteamento — sempre faz RAG + análise.

#### Tratamento de RAG opcional
- Em [dsa_p8_streamlit_app.py:69-77](projetos_8_modulo_2/dsa_p8_streamlit_app.py#L69-L77): se o índice FAISS não existe, mostra warning e prossegue **sem RAG** — usa só a imagem + pergunta. Padrão de degradação graciosa.

### 🏗️ Arquitetura / Fluxo

```
SETUP (dsa_p8_setup_rag.py):
    dsa_pdfs_contabilidade/*.pdf
        │
        ▼ PyPDFDirectoryLoader + RecursiveCharacterTextSplitter(1000, 150)
        ▼ FastEmbedEmbeddings(BAAI/bge-small-en-v1.5)
        ▼ FAISS.from_documents().save_local("dsa_faiss_index_contabilidade")
    (Caso pasta vazia: cria índice FAISS vazio com IndexFlatL2)

APP (dsa_p8_streamlit_app.py):
    Upload imagem (PNG/JPG/WEBP)  +  Pergunta texto
        │                                │
        └────────────┬───────────────────┘
                     ▼
        LangGraph StateGraph(MultimodalGraphState):

        ┌────────────────────────┐
        │ retrieve_rag_node      │   query → retriever.invoke (k=3)
        │                        │   → state["rag_context"]
        └───────────┬────────────┘
                    │
                    ▼
        ┌────────────────────────┐   message_content = [
        │ analyze_invoice_node   │     {"type":"text", "text": prompt+rag_context+query},
        │                        │     {"type":"image_url", "image_url": data:URL base64}
        │  Gemini Flash Vision   │   ]
        │  (temperature=0.2)     │   llm.invoke([HumanMessage(content=message_content)])
        │                        │   → state["final_answer"]
        └───────────┬────────────┘
                    │
                    ▼
                   END
                    │
                    ▼ dsa_clean_llm_output (remove caracteres invisíveis)
                    ▼
            st.markdown("<pre>{cleaned}</pre>")
            + st.expander("Saída crua")
            + st.expander("Contexto RAG")
```

### 💡 Conceitos-Chave Aprendidos
- **Multimodal RAG**: combinar imagem + RAG textual em um único prompt LLM.
- **Encoding base64 inline**: padrão data URL aceito por LLMs multimodais (Gemini, GPT-4o).
- **Degradação graciosa do RAG**: app continua útil mesmo sem índice (só análise pura de imagem).
- **Limpeza pós-LLM**: caracteres invisíveis e diacríticos não-padronizados são realidade — sempre limpe antes de exibir.
- **State típico multimodal**: `{query, image_bytes, image_mime_type, rag_context, final_answer}`.

### ⚠️ Pontos de Atenção
- **Modelo Gemini "latest"**: `gemini-flash-latest` é alias instável; em produção, fixe versão (`gemini-1.5-flash-002`).
- **Tamanho da imagem**: Gemini comprime imagens grandes — verifique resolução suficiente para valores monetários e códigos.
- **Privacidade de notas fiscais**: documentos contábeis contêm CPF/CNPJ; ao usar Gemini API, esses dados saem do seu ambiente. Para prod, considere on-prem (LLaVA, Idefics).
- **Prompt instrui anomalias**: "procure por inconsistências comuns (datas, valores, cálculos, informações obrigatórias ausentes)" — útil mas pode ter falso-positivo. Valide sempre.
- **Pasta `scratch/`** contém `list_models.py` (script ad-hoc).
- **Nome de arquivo no warning** ([dsa_p8_streamlit_app.py:73](projetos_8_modulo_2/dsa_p8_streamlit_app.py#L73)) refere-se a `setup_rag_accounting.py` mas o nome real é `dsa_p8_setup_rag.py` — texto desatualizado.

### 🔗 Conexão com outros projetos
- **LangGraph** + **FAISS persistido** + **FastEmbed**: mesma stack do P7, mas:
  - P7: roteamento RAG/WEB; P8: multimodal direto.
  - P7: Groq; P8: Google Gemini.
- Único projeto **multimodal** da pós.
- Único projeto que usa **Google Gemini**.
- Padrão `setup_rag.py` + `streamlit_app.py` como no P7.

---

## 📚 Glossário Técnico

| Termo | Definição |
|---|---|
| **Agentic RAG** | RAG implementado como um agente (LangGraph), com nós/decisões — não pipeline linear. |
| **BM25** | Algoritmo de ranking léxico do ElasticSearch; pondera frequência do termo + raridade no corpus. |
| **Chunk / Split** | Pedaço menor de um documento gerado por um text splitter para caber no contexto do LLM. |
| **`condense_question`** | Modo de chat do LlamaIndex que reformula a pergunta atual considerando o histórico antes do retrieval. |
| **Cosine similarity / Distância cosseno** | Métrica entre vetores baseada no ângulo (não na magnitude). Padrão para embeddings textuais. |
| **DAG** | Directed Acyclic Graph; representação de pipelines no Airflow. |
| **Embedding** | Representação vetorial densa de texto que captura semântica. |
| **Extractive QA** | Modelo que retorna span do contexto (recorte literal), não gera texto novo (ex: BERT-SQuAD). |
| **FAISS** | Vector store em memória (Facebook AI). |
| **Few-shot prompting** | Incluir N exemplos de input→output no prompt para guiar a resposta. |
| **GraphRAG** | Variante de RAG onde os chunks formam um grafo e o retrieval traverse o grafo. |
| **Groq** | Plataforma de inferência LLM com hardware LPU; latências sub-segundo. |
| **Hit Rate** | Métrica de retrieval: fração de consultas onde algum doc relevante apareceu no top-k. |
| **`IndexFlatL2`** | Índice FAISS exato com distância L2; sem aproximação. |
| **LangGraph** | Lib para construir workflows de agentes como grafos de estado. |
| **LCEL** | LangChain Expression Language; composição funcional `prompt \| llm \| parser`. |
| **Lematização** | Normalização morfológica (ex: "running" → "run"). Diferente de stemming. |
| **LLMOps** | Disciplina de operar LLMs em produção (CI/CD, monitoring, eval). |
| **LLM Routing** | Padrão onde um SLM/LLM rápido decide para qual fonte de dados/modelo enviar a query. |
| **MD5 truncado (8 chars)** | Hash determinístico curto usado como ID de documento. |
| **MRR (Mean Reciprocal Rank)** | Métrica de retrieval: média de `1/(posição do primeiro relevante)`. |
| **Multimodal** | Modelo/sistema que aceita múltiplas modalidades (texto + imagem + áudio...). |
| **Ollama** | Runtime local para LLMs open-source. |
| **Prompt template** | Texto parametrizado (`{context}`, `{question}`) usado para gerar prompts. |
| **Qdrant** | Banco vetorial em Rust; suporta in-memory e cliente-servidor. |
| **RAG (Retrieval-Augmented Generation)** | Padrão de buscar contexto relevante antes de gerar a resposta. |
| **`RecursiveCharacterTextSplitter`** | Text splitter do LangChain que tenta separar por separadores hierárquicos. |
| **`RealDictCursor`** | Cursor psycopg2 que retorna dicts em vez de tuplas. |
| **SLM** | Small Language Model (até ~7B params); ex: TinyLlama, Gemma 4B. |
| **`StateGraph`** | Classe LangGraph para definir grafos com estado tipado (`TypedDict`). |
| **Streamlit `@st.cache_resource`** | Decorator para cachear objetos pesados (LLMs, índices) entre re-runs. |
| **`TypedDict`** | Tipagem de dicionário do Python; usada como contrato de estado em LangGraph. |
| **Vector store** | Base que armazena embeddings + permite busca por similaridade. |
| **WordNet** | Banco lexical do inglês usado pelo NLTK para lematização e sinônimos. |

---

## 🗺️ Mapa de Tecnologias

| Tecnologia | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 |
|---|---|---|---|---|---|---|---|---|
| **Streamlit** | ✅ | | | ✅ | ✅ | | ✅ | ✅ |
| **FastAPI** | | ✅ | | | | | | |
| **Gradio** | | | ✅ | | | | | |
| **Docker / Compose** | ✅ | | | | | | | |
| **Apache Airflow** | ✅ | | | | | | | |
| **PostgreSQL** | ✅ | | | | | | | |
| **SQLite** | | ✅ | | | | | | |
| **ElasticSearch** | ✅ | | | | | | | |
| **Qdrant** | | | ✅ | | | | | |
| **FAISS** | | | | | ✅ | ✅ | ✅ | ✅ |
| **NetworkX** | | | | | ✅ | | | |
| **LangChain** | | | | ✅ | ✅ | ✅ | ✅ | ✅ |
| **LangGraph** | | | | | | ✅ | ✅ | ✅ |
| **LlamaIndex** | | | | ✅ | | | | |
| **Sentence Transformers** | | | ✅ | | | | | |
| **HuggingFaceEmbeddings (LC)** | | | | ✅ | | ✅ | | |
| **FastEmbed (BGE)** | | | | | | | ✅ | ✅ |
| **OpenAI text-embedding-3-small** | | | | | ✅ | | | |
| **HuggingFace Inference API (BERT)** | ✅ | | | | | | | |
| **OpenAI GPT-4o** | | ✅ | | | | | | |
| **OpenAI GPT-4o-mini** | | | | | ✅ | | | |
| **Groq Llama 3.3 70B** | | | | | | ✅ | ✅ | |
| **Groq Llama 3.1 8B Instant** | | | | | | | ✅ | |
| **Google Gemini Flash** | | | | | | | | ✅ |
| **Ollama (gemma3:4b)** | | | | ✅ | | | | |
| **TinyLlama-1.1B (transformers)** | | | ✅ | | | | | |
| **DuckDuckGoSearchRun** | | | | | | | ✅ | |
| **PyPDFLoader / Directory** | | | | | ✅ | ✅ | ✅ | ✅ |
| **docx2txt / SimpleDirectoryReader** | | | | ✅ | | | | |
| **Grafana** | ✅ | | | | | | | |
| **NLTK + WordNet** | | | | | ✅ | | | |
| **`RecursiveCharacterTextSplitter`** | | | | | ✅ | ✅ | ✅ | ✅ |
| **`@asynccontextmanager` (FastAPI)** | | ✅ | | | | | | |
| **CUDA / device_map="cuda"** | | | ✅ | | | | | |

---

## 🧭 Guia de Decisão Rápida

### "Preciso fazer Q&A sobre PDFs em produção, com baixa latência."
- **Stack**: FAISS local + FastEmbed (`BAAI/bge-small-en-v1.5`) + Groq Llama 3.3 70B + LangGraph linear.
- **Veja**: P6 (CLI) ou P7 (Streamlit + roteamento).
- **Por quê**: FastEmbed dispensa torch; Groq tem latência <1s; LangGraph isola retrieval/generation.

### "Preciso de Q&A sobre dados estruturados (clientes, pacientes, produtos)."
- **Stack**: FastAPI + SQLite/Postgres + OpenAI GPT-4o.
- **Veja**: P2.
- **Por quê**: Quando os dados já estão em SQL, embeddings são overkill — `SELECT` + LLM montado como prompt já resolve.

### "Preciso de privacidade absoluta (dados sensíveis não podem sair do servidor)."
- **Stack**: Ollama (gemma3:4b ou llama3) + LlamaIndex + HuggingFaceEmbeddings (`all-MiniLM-L6-v2`) + Streamlit.
- **Veja**: P4.
- **Por quê**: Ollama roda 100% local; nenhum byte sai para nuvem.

### "Preciso analisar imagens (notas fiscais, contratos digitalizados, screenshots)."
- **Stack**: Google Gemini Flash + LangGraph (RAG opcional) + FastEmbed + FAISS.
- **Veja**: P8.
- **Por quê**: Gemini é multimodal nativo e barato; janela de contexto grande para combinar manual + imagem.

### "Preciso de uma POC didática rodando em GPU pequena (Colab free)."
- **Stack**: Qdrant in-memory + Sentence Transformers + TinyLlama + Gradio.
- **Veja**: P3.
- **Por quê**: Tudo em RAM; TinyLlama cabe em 4GB de VRAM; Gradio gera tunnel público gratuito.

### "Preciso de pipeline LLMOps completo (ingestão automatizada + observabilidade + feedback loop)."
- **Stack**: Docker Compose + Airflow + ElasticSearch (ou FAISS) + Postgres + LLM (BERT/Llama/GPT) + Streamlit + Grafana.
- **Veja**: P1.
- **Por quê**: Cada componente é industry-standard; padrão de produção real.

### "Preciso navegar em relações semânticas profundas dentro de um documento (não só top-k)."
- **Stack**: GraphRAG: NetworkX + FAISS + OpenAI embeddings + GPT-4o-mini + lematização NLTK.
- **Veja**: P5.
- **Por quê**: Top-k clássico falha em perguntas que exigem agregar informações dispersas; o grafo segue conceitos compartilhados.

### "Preciso decidir dinamicamente qual fonte usar (RAG interno vs busca web)."
- **Stack**: LangGraph com `add_conditional_edges` + dois LLMs (SLM para rotear + LLM grande para responder) + DuckDuckGoSearchRun.
- **Veja**: P7.
- **Por quê**: LLM Routing economiza custo (usa SLM para decisões) e mantém o sistema atual sem reindexar a cada notícia.

### "Preciso construir uma API REST que use LLM (não app web)."
- **Stack**: FastAPI + Gunicorn + Uvicorn + Pydantic + OpenAI/qualquer LLM SDK + python-dotenv.
- **Veja**: P2.
- **Por quê**: FastAPI dá tipagem + docs automáticas; Gunicorn paraleliza.

### "Quero entender só o mínimo de RAG, sem complicação."
- **Stack**: Sentence Transformers + Qdrant in-memory + qualquer LLM via API.
- **Veja**: P3 (módulo de retrieval).
- **Por quê**: 30 linhas mostram encode → store → search → augment → generate.

---

*Documento gerado a partir da análise direta dos códigos-fonte dos projetos 1-8 do Módulo 2.*

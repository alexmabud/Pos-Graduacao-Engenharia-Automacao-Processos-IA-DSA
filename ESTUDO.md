# ESTUDO.md - Caderno de Estudos de Engenharia de Software e IA

Este arquivo é o seu guia mestre de aprendizado, cobrindo todos os módulos da sua Pós-Graduação em Engenharia de Automação de Processos com IA.

---

## 1. Visão Geral do Projeto
O projeto está estruturado em dois grandes blocos de competências que conectam a base operacional à inteligência avançada:
1.  **Módulo 1: Automação, Excel e Engenharia de Dados**: Base sólida de manipulação de dados em massa e automação de sistemas.
2.  **Módulo 2: Inteligência Aumentada**: Implementação de arquiteturas Generativas e operacionalização (LLMOps).

---

## 2. Mapa do Projeto (Estrutura de Conteúdo)

### Módulo 1: Automação & Engenharia de Dados (11 Unidades)
- **Engenharia com Pandas (Unidades 1-3)**: Foco em limpeza e tratamento estatístico.
- **Automação OS e Web (Unidades 4-7)**: Uso de scripts para interagir com o sistema e capturar dados via Selenium/Scraping.
- **Excel Avançado com IA (Unidades 8-11)**: A evolução da automação tradicional usando LLMs para análise.

### Módulo 2: Inteligência Aumentada (Capítulos 1-2)
- **RAG Local vs Profissional**: Implementações experimentais (DeepSeek) e corporativas (ElasticSearch).
- **LLMOps**: Gestão do ciclo de vida dos modelos em containers Docker.

---

## 3. Caderno de Conceitos (Explicações Detalhadas)

### 3.1 Engenharia de Dados & ETL
O processo de **ETL (Extract, Transform, Load)** é a espinha dorsal da automação:
- **Extração**: Pode ser via `xl()` do Excel, `pd.read_csv()` ou Selenium simulando um clique humano.
- **Transformação (A Alma do Engenheiro)**:
    - **Imputação de Dados**: Preencher buracos (`NaN`) usando a **Mediana** (para números, evita distorção por outliers) ou a **Moda** (para textos, usa o valor mais frequente).
    - **Casting e Regex**: Converter textos como "$1.000,00" para números fluates (`1000.0`) usando expressões regulares para limpar caracteres não numéricos.
- **Carga**: Salvar o resultado final em um novo Excel, Banco de Dados (PostgreSQL) ou enviar para o motor de busca (ElasticSearch).

### 3.2 IA Generativa e RAG (Retrieval-Augmented Generation)
O RAG resolve o problema das "Alucinações" dos LLMs:
- **Embeddings**: Transformam palavras em vetores (listas de números). Quanto mais próximos os vetores, mais similar é o sentido das palavras.
- **Vector Stores (FAISS vs Elastic)**:
    - **FAISS**: Memória rápida, ótima para projetos locais ou individuais.
    - **ElasticSearch**: Robusto, escalável, permite buscas complexas (multi-match) em grandes empresas.
- **Semantic Chunking**: Em vez de cortar o texto a cada 500 palavras, o divisor espera o assunto mudar para criar um novo bloco, mantendo a coesão da resposta da IA.

### 3.3 LLMOps e Orquestração
- **Docker Compose**: Orquestra vários "mini-computadores" (containers) para trabalharem juntos. Essencial para que o Streamlit consiga conversar com o PostgreSQL sem erros de rede.
- **Airflow**: Age como um "despertador inteligente". Ele sabe que a tarefa B só pode começar quando a tarefa A (extração de dados) terminar com sucesso.

---

## 4. Melhores Práticas de Engenharia (Dicas do Professor)
- **Idempotência**: Seus scripts devem poder rodar 100 vezes sem criar duplicatas. O uso de **MD5 Hashing** para gerar IDs de documentos é a técnica recomendada aqui.
- **Deep Copy**: Ao manipular DataFrames, use sempre `.copy()` para evitar que o Python altere o dado original inesperadamente.
- **Boosting na Busca**: No ElasticSearch, use o sinal `^` (ex: `question^2`) para dar mais peso a campos que você sabe que são mais importantes para a resposta.

---

## 5. Dúvidas Respondidas

- **Por que preencher vazios com Mediana e não com Média?**
  *Resposta:* A média é "puxada" por valores muito altos. Se você tem 4 pessoas que ganham R$ 2.000 e uma que ganha R$ 100.000, a média será irreal. A mediana mantém o pé no chão.

- **Qual a diferença entre o RAG do Módulo 1 e do Módulo 2?**
  *Resposta:* O do Módulo 1 é focado em automação pontual de documentos internos. O do Módulo 2 é uma arquitetura preparada para produção, com monitoramento de métricas como Hit Rate e MRR.

- **Onde devo inserir minha chave do Hugging Face no projeto?**
  *Resposta:* A chave deve ser colada na linha 189 do arquivo `docker-compose.yaml`, dentro da variável de ambiente `HUGGINGFACE_KEY` do serviço `app`.

---

## 6. Registro de Análise de Arquivos

| Arquivo Analisado | Lições Aprendidas |
| :--- | :--- |
| `projeto_7_...` | Técnicas de limpeza de moeda e imputação estatística (Moda/Mediana). |
| `dsarag.py` | Implementação de RAG local com DeepSeek e Semantic Chunking. |
| `appdsa.py` | Gestão de estado no Streamlit e loop de feedback do usuário. |
| `dsallm.py` | Integração de APIs de inferência e hashing determinístico de conteúdo. |
| `docker-compose.yaml` | Orquestração de containers para LLMOps, incluindo Airflow, ElasticSearch e a aplicação principal. |


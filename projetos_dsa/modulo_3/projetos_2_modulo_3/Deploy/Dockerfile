# Projeto 2 - Construção de Multi-Agentes de IA com CrewAI e Deploy via API com Docker

# Usa uma imagem base do Python
FROM python:3.12

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos do projeto para o container
COPY . .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta da API
EXPOSE 8000

# Comando para rodar o servidor FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

# Projeto 2 - Construção de Multi-Agentes de IA com CrewAI e Deploy via API com Docker

# Imports
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from dsa_time_agentes import dsa_execute_time_agentes  # Importando a função do script principal

# Cria a aplicação FastAPI
app = FastAPI()

# Modelo de entrada
class TopicRequest(BaseModel):
    topic: str

@app.post("/execute")
def dsa_executa_agentes(request: TopicRequest):
    resultado = dsa_execute_time_agentes(request.topic)
    return {"result": resultado}

# Execução local
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

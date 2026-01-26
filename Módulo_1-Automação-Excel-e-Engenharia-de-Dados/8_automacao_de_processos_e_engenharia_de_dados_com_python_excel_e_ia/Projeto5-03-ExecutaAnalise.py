# Projeto 5 - Detecção Automática de Anomalias em Logs de Pipelines de Dados
# Módulo de Execução da Análise

# Imports
import subprocess

# Função para executar outros scripts Python
def dsa_run_pipeline(script_name):
    try:
        result = subprocess.run(['python', script_name], check=True, capture_output=True, text=True)
        print(f"\nScript {script_name} executado com sucesso.")
        print("\nSaída:\n", result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"\nErro ao executar o script {script_name}.")
        print("\nErro:\n", e.stderr)

# Lista de scripts
scripts = [
    'Projeto5-01-ValidaArquivo.py',
    'Projeto5-02-AnalisaArquivo.py'
]

# Executa os scripts em um loop
for script in scripts:
    dsa_run_pipeline(script)


print(f"\nPipeline executado com sucesso.\n")

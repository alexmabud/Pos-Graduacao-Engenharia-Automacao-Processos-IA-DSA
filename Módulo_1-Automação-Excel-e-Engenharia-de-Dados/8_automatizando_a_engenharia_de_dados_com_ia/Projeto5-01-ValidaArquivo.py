# Projeto 5 - Detecção Automática de Anomalias em Logs de Pipelines de Dados
# Módulo de Validação de Arquivo

# Import
import pandas as pd

# Caminho para o arquivo
file_path = "logs_pipeline.xlsx"

# Função para verificar se o arquivo é válido e contar o número de linhas
def dsa_valida_arquivo(file_path):

    try:
        
        # Tenta carregar o arquivo Excel
        df = pd.read_excel(file_path)
        
        # Verifica se o DataFrame contém dados
        if df.empty:
            return "O arquivo está vazio."
        
        # Conta o número de linhas
        num_rows = df.shape[0]
        
        return f"O arquivo é válido e contém {num_rows} linhas."
    
    except Exception as e:
        return f"Ocorreu um erro ao tentar ler o arquivo: {str(e)}"

# Executa a função
resultado = dsa_valida_arquivo(file_path)
print(resultado)

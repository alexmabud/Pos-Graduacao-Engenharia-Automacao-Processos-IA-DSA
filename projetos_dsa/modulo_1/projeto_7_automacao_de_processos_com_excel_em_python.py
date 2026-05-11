"""
Projeto 7 - Automatizando a Limpeza e Transformação de Dados com Python Dentro do Excel

Este script demonstra como usar Python para automatizar tarefas de limpeza e transformação
de dados diretamente no Excel, eliminando processos manuais repetitivos.

Requisitos:
- xlwings ou biblioteca similar para integração Python-Excel
- pandas para manipulação de dados
- Excel instalado (Windows/Mac)

Como funciona:
1. O código é executado dentro de uma célula do Excel como função UDF (User Defined Function)
2. Os dados são lidos do Excel, processados em Python e retornados ao Excel
3. Todos os cálculos e transformações ocorrem em tempo real
"""

"""
# ===================================================================================
# ETAPA 1: IMPORTAÇÃO DOS DADOS DO EXCEL
# ===================================================================================
# xl("A1:H21", headers=True) - Lê dados de uma planilha Excel
# - "A1:H21": Define o intervalo de células (da coluna A até H, linhas 1 a 21)
# - headers=True: Informa que a primeira linha contém os nomes das colunas
# - Retorna um DataFrame pandas com os dados da planilha
#
# COMO FAZER NO EXCEL:
# 1. Abra o Excel e selecione o intervalo A1:H21
# 2. Execute este script via xlwings ou add-in Python
# 3. Os dados serão carregados automaticamente em um DataFrame
df = xl("A1:H21", headers=True)

# ===================================================================================
# ETAPA 2: ANÁLISE ESTATÍSTICA DESCRITIVA - DADOS NUMÉRICOS
# ===================================================================================
# df.describe() - Gera estatísticas descritivas das colunas numéricas
# Retorna: contagem, média, desvio padrão, mínimo, quartis (25%, 50%, 75%) e máximo
#
# RESULTADO NO EXCEL:
# - Cada estatística aparece em uma linha
# - Cada coluna numérica tem suas estatísticas calculadas
# - Útil para identificar outliers, tendências centrais e dispersão dos dados
df.describe()

# ===================================================================================
# ETAPA 3: ANÁLISE ESTATÍSTICA DESCRITIVA - DADOS CATEGÓRICOS (TEXTO)
# ===================================================================================
# df.describe(include=['object']) - Analisa apenas colunas de texto/categorias
# Retorna: contagem, valores únicos, valor mais frequente (top) e sua frequência
#
# RESULTADO NO EXCEL:
# - Mostra quantos valores diferentes existem em cada coluna de texto
# - Identifica qual categoria aparece mais vezes
# - Ajuda a entender a distribuição de dados categóricos (ex: cidades, produtos)
df.describe(include=['object'])

# ===================================================================================
# ETAPA 4: IDENTIFICAÇÃO DE VALORES AUSENTES (CÉLULAS VAZIAS)
# ===================================================================================
# df.isna().sum() - Conta quantas células estão vazias em cada coluna
# - isna(): Retorna True para células vazias, False para células preenchidas
# - sum(): Soma os valores True (conta quantas células estão vazias)
#
# RESULTADO NO EXCEL:
# - Mostra o número de células vazias por coluna
# - Exemplo: Se "Idade" tem 3 células vazias, retorna "Idade: 3"
# - Essencial para saber quais colunas precisam de tratamento
df.isna().sum()

# ===================================================================================
# ETAPA 5: SEPARAÇÃO DE COLUNAS NUMÉRICAS
# ===================================================================================
# df.select_dtypes(include='number') - Filtra apenas colunas com números
# - Separa colunas como: Idade, Salário, Quantidade, Preço, etc.
# - Exclui colunas de texto como: Nome, Cidade, Categoria, etc.
#
# POR QUE FAZER ISSO?
# - Colunas numéricas e de texto precisam de tratamentos diferentes
# - Valores ausentes em números são preenchidos com mediana/média
# - Valores ausentes em texto são preenchidos com moda (valor mais comum)
numerical_cols = df.select_dtypes(include='number')

# ===================================================================================
# ETAPA 6: PREENCHIMENTO DE VALORES AUSENTES - DADOS NUMÉRICOS
# ===================================================================================
# fillna(numerical_cols.median()) - Preenche células vazias com a mediana
# - median(): Valor do meio quando os dados estão ordenados
# - Menos sensível a outliers que a média
#
# EXEMPLO PRÁTICO:
# Se a coluna "Idade" tem valores: 25, 30, [vazio], 35, 40
# A mediana é 32.5 (média de 30 e 35)
# O valor vazio será preenchido com 32.5
#
# RESULTADO NO EXCEL:
# - Todas as células vazias em colunas numéricas ficam preenchidas
# - Mantém a consistência estatística dos dados
df_numericas = numerical_cols.fillna(numerical_cols.median())

# ===================================================================================
# ETAPA 7: VERIFICAÇÃO DE VALORES AUSENTES - DADOS NUMÉRICOS
# ===================================================================================
# Confirma que não há mais células vazias nas colunas numéricas
# Deve retornar 0 para todas as colunas após o preenchimento
df_numericas.isna().sum()

# ===================================================================================
# ETAPA 8: SEPARAÇÃO DE COLUNAS CATEGÓRICAS (TEXTO)
# ===================================================================================
# df.select_dtypes(include=['object', 'category']) - Filtra apenas colunas de texto
# - 'object': Texto comum (Nome, Endereço, Descrição)
# - 'category': Categorias definidas (Departamento, Status, Tipo)
#
# EXEMPLOS DE COLUNAS CATEGÓRICAS:
# - Nome do Cliente, Cidade, Estado, Categoria do Produto, Departamento
categorical_cols = df.select_dtypes(include=['object', 'category'])

# ===================================================================================
# ETAPA 9: VERIFICAÇÃO DE VALORES AUSENTES - DADOS CATEGÓRICOS
# ===================================================================================
# Mostra quantas células vazias existem em cada coluna de texto
# antes do preenchimento
categorical_cols.isna().sum()

# ===================================================================================
# ETAPA 10: CRIAÇÃO DE CÓPIA DO DATAFRAME CATEGÓRICO
# ===================================================================================
# .copy() - Cria uma cópia independente dos dados categóricos
# - Evita modificar o DataFrame original acidentalmente
# - Boa prática de programação para segurança dos dados
df_categorical = categorical_cols.copy()

# ===================================================================================
# ETAPA 11: PREENCHIMENTO DE VALORES AUSENTES - DADOS CATEGÓRICOS
# ===================================================================================
# fillna(col.mode()[0]) - Preenche células vazias com a moda (valor mais frequente)
# - mode(): Retorna o valor que aparece mais vezes
# - [0]: Pega o primeiro valor da moda (caso haja empate)
#
# EXEMPLO PRÁTICO:
# Se a coluna "Departamento" tem: TI, TI, [vazio], RH, TI, RH
# A moda é "TI" (aparece 3 vezes)
# O valor vazio será preenchido com "TI"
#
# RESULTADO NO EXCEL:
# - Células vazias em colunas de texto recebem o valor mais comum
# - Mantém a distribuição estatística dos dados
df_categorical = df_categorical.apply(lambda col: col.fillna(col.mode()[0]))

# ===================================================================================
# ETAPA 12: VERIFICAÇÃO FINAL - DADOS CATEGÓRICOS
# ===================================================================================
# Confirma que não há mais células vazias nas colunas de texto
# Deve retornar 0 para todas as colunas
df_categorical.isna().sum()

# ===================================================================================
# ETAPA 13: LIMPEZA E CONVERSÃO DA COLUNA "RENDA"
# ===================================================================================
# replace('[\$,]', '', regex=True) - Remove símbolos de dólar ($) e vírgulas (,)
# astype(float) - Converte texto para número decimal
#
# EXEMPLO DE TRANSFORMAÇÃO:
# Antes: "$1,500.00"  →  Depois: 1500.00 (número)
# Antes: "$25,000"    →  Depois: 25000.00 (número)
#
# POR QUE É NECESSÁRIO?
# - Excel pode armazenar valores monetários como texto
# - Para fazer cálculos, precisamos converter para número
# - Remove formatação que impede operações matemáticas
df_numericas['Renda'] = df_numericas['Renda'].replace('[\$,]', '', regex=True).astype(float)

# ===================================================================================
# ETAPA 14: CRIAÇÃO DE NOVA COLUNA "BONUS"
# ===================================================================================
# df_numericas['Bonus'] = df_numericas['Renda'] * 0.10
# - Cria uma nova coluna calculando 10% do valor da Renda
# - Multiplica cada valor por 0.10 (equivalente a 10%)
#
# EXEMPLO PRÁTICO:
# Se Renda = $5,000.00  →  Bonus = $500.00
# Se Renda = $8,500.00  →  Bonus = $850.00
#
# RESULTADO NO EXCEL:
# - Uma nova coluna "Bonus" aparece ao lado das colunas numéricas
# - Todos os valores são calculados automaticamente
df_numericas['Bonus'] = df_numericas['Renda'] * 0.10

# ===================================================================================
# ETAPA 15: VISUALIZAÇÃO DAS PRIMEIRAS LINHAS
# ===================================================================================
# df_numericas.head() - Mostra as 5 primeiras linhas do DataFrame numérico
# - Útil para verificar se as transformações foram aplicadas corretamente
# - Retorna ao Excel para visualização
df_numericas.head()

# ===================================================================================
# ETAPA 16: COMBINAÇÃO DOS DADOS NUMÉRICOS E CATEGÓRICOS
# ===================================================================================
# pd.concat([df_numericas, df_categorical], axis=1)
# - Junta os DataFrames lado a lado (axis=1 significa por colunas)
# - axis=0 seria empilhar linhas; axis=1 é adicionar colunas
#
# RESULTADO NO EXCEL:
# - Um DataFrame completo com TODAS as colunas:
#   * Colunas numéricas (com valores ausentes preenchidos + coluna Bonus)
#   * Colunas categóricas (com valores ausentes preenchidos)
# - Dados prontos para análise ou relatório final
df_final = pd.concat([df_numericas, df_categorical], axis=1)

# ===================================================================================
# ETAPA 17: VISUALIZAÇÃO DO RESULTADO FINAL
# ===================================================================================
# df_final.head(20) - Mostra as 20 primeiras linhas do DataFrame final
# - Exibe o resultado de todo o processo de limpeza e transformação
# - Este DataFrame será exibido no Excel
#
# O QUE VOCÊ VERÁ NO EXCEL:
# - Dados limpos (sem células vazias)
# - Coluna "Renda" formatada como número
# - Nova coluna "Bonus" calculada
# - Todas as transformações aplicadas e prontas para uso
df_final.head(20)

"""



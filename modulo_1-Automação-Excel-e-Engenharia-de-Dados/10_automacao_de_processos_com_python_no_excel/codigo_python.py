# Projeto 7 - Automatizando a Limpeza e Transformação de Dados com Python Dentro do Excel

df = xl("A1:H21", headers=True)

df.describe()

df.describe(include=['object'])

df.isna().sum()

# Selecionar apenas as colunas numéricas
numerical_cols = df.select_dtypes(include='number')

# Imputação de valores ausentes com a mediana
df_numericas = numerical_cols.fillna(numerical_cols.median())

df_numericas.isna().sum()

# Selecionar apenas as colunas categóricas
categorical_cols = df.select_dtypes(include=['object', 'category'])

categorical_cols.isna().sum()

# Criar um novo DataFrame apenas com as variáveis categóricas
df_categorical = categorical_cols.copy()

# Preencher os valores ausentes com a moda de cada coluna categórica
df_categorical = df_categorical.apply(lambda col: col.fillna(col.mode()[0]))

df_categorical.isna().sum()

# Remover o símbolo de dólar e as vírgulas, e converter para numérico
df_numericas['Renda'] = df_numericas['Renda'].replace('[\$,]', '', regex=True).astype(float)

# Criar a nova coluna "bonus" com 10% da coluna "Renda"
df_numericas['Bonus'] = df_numericas['Renda'] * 0.10

# Exibir o DataFrame com a nova coluna
df_numericas.head()

# Concatenar os dois DataFrames (numéricos e categóricos)
df_final = pd.concat([df_numericas, df_categorical], axis=1)

# Exibir todas as linhas e colunas (usar a saída como Excel Value)
df_final.head(20)





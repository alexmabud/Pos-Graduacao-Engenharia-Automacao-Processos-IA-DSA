# Projeto 6 - Automatizando a Geração de Relatórios Financeiros com Word, PDF, Excel e Python

# Imports necessários para o script funcionar
import os  # Manipulação de diretórios e arquivos
import pdfplumber  # Extração de texto e tabelas de PDFs
import pandas as pd  # Manipulação e análise de dados em formato de tabelas
import tkinter as tk  # Interface gráfica para seleção de arquivos e locais de salvamento
from PyPDF2 import PdfReader  # Leitura de arquivos PDF
from docx import Document  # Manipulação de documentos Word
from tkinter import filedialog  # Caixas de diálogo para seleção de arquivos
from tkinter import messagebox  # Caixas de mensagem para alertas e informações
from tkinter import ttk  # Importar ttk para estilos aprimorados

# Função para padronizar os cabeçalhos das tabelas
def dsa_padroniza_header(header):
    
    # Retorna vazio se não tiver cabeçalho na tabela
    if not header:
        return []
    
    # Remove espaços em branco, quebra de linhas e converte para minúsculas
    return [col.strip().lower().replace("\n", " ") if col else '' for col in header]

# Função para verificar e renomear colunas duplicadas em um DataFrame
def dsa_verifica_coluna_unica(columns):
    
    # Dicionário para tratar colunas com nomes duplicados (se tiver)
    seen = {}
    
    # Adiciona sufixos para colunas duplicadas
    for i, col in enumerate(columns):
        if col in seen:
            seen[col] += 1
            columns[i] = f"{col}_{seen[col]}"
        else:
            seen[col] = 0
    
    return columns

# Função para alinhar colunas de um DataFrame com um DataFrame combinado
def dsa_limpa_alinha_tabela(df, combined_df):
    
    df.columns = dsa_verifica_coluna_unica(list(df.columns))
    
    # Adiciona colunas ausentes com valores vazios
    for col in combined_df.columns:
        if col not in df.columns:
            df[col] = ''
    
    # Reorganiza as colunas de acordo com o DataFrame combinado
    df = df[combined_df.columns]
    
    return df

# Função para remover linhas em branco de um DataFrame
def dsa_remove_linhas_branco(df):
    
    # Remove linhas onde todos os valores são NaN
    df = df.dropna(how='all')  
    
    # Remove linhas onde a primeira célula está vazia ou é nula
    df = df[df.iloc[:, 0].notna() & (df.iloc[:, 0] != '')]
    
    return df

# Função para converter tabelas de PDF para Excel
def dsa_converte_pdf_excel(pdf_path, excel_path):
    
    print(f"Pasta do PDF: {pdf_path}")  # Exibe o caminho do PDF
    print(f"Pasta do Excel: {excel_path}")  # Exibe o caminho onde o Excel será salvo

    # Verifica se é possível escrever na pasta de destino
    if not os.access(os.path.dirname(excel_path), os.W_OK):
        raise PermissionError(f"Não é possível gravar na pasta: {os.path.dirname(excel_path)}")

    # Lê o PDF
    reader = PdfReader(pdf_path)  

    # Dicionário para armazenar tabelas organizadas por cabeçalho
    tables_by_header = {}  

    # Abre o PDF para extração de tabelas
    with pdfplumber.open(pdf_path) as pdf:  

        # Itera por cada página
        for page_num, page in enumerate(pdf.pages):  

            # Extrai tabelas da página
            tables = page.extract_tables()  

            for table in tables:
                
                # Verifica se a tabela é válida
                if table and len(table) > 1 and table[0]:

                    # Padroniza o cabeçalho da tabela
                    header = dsa_padroniza_header(table[0])  
                    header_tuple = tuple(header)
                    
                    # Verifica se o cabeçalho é válido
                    if any(header):

                        # Cria um DataFrame com os dados da tabela
                        df = pd.DataFrame(table[1:], columns=header)  

                        # Verifica colunas duplicadas
                        df.columns = dsa_verifica_coluna_unica(list(df.columns))  

                        # Exibe os títulos das colunas
                        print(f"Página {page_num + 1} títulos das colunas: {header}")  
                        
                        # Concatena a tabela com outras tabelas do mesmo cabeçalho
                        if header_tuple in tables_by_header:
                            df = dsa_limpa_alinha_tabela(df, tables_by_header[header_tuple])
                            tables_by_header[header_tuple] = pd.concat([tables_by_header[header_tuple], df], ignore_index=True)
                        else:
                            tables_by_header[header_tuple] = df
                    else:
                        print(f"Pular uma tabela na página {page_num + 1} devido a cabeçalho inválido ou vazio.")
                else:
                    print(f"Pular uma tabela na página {page_num + 1} devido a dados ausentes ou inválidos.")

    # Verifica se há tabelas extraídas
    if tables_by_header:

        try:
            
            # Salva as tabelas extraídas em um arquivo Excel
            with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
                
                for i, (header_tuple, combined_table) in enumerate(tables_by_header.items()):
                    combined_table.columns = dsa_verifica_coluna_unica(list(combined_table.columns))
                    combined_table = dsa_remove_linhas_branco(combined_table)
                    sheet_name = f"Tabela_{i+1}"
                    combined_table.to_excel(writer, sheet_name=sheet_name, index=False)
            messagebox.showinfo("Sucesso", f"As tabelas foram extraídas e salvas com sucesso em {excel_path}")
        except Exception as e:
            print(f"Falha ao salvar o arquivo Excel: {e}")
            messagebox.showerror("Erro", f"Falha ao salvar o arquivo Excel: {e}")
    else:
        messagebox.showinfo("Nenhuma Tabela Encontrada", "Não há tabela no arquivo PDF.")

# Função para converter tabelas de DOCX para Excel
def dsa_converte_docx_excel(docx_path, excel_path):
    
    print(f"Pasta do DOCX: {docx_path}")  # Exibe o caminho do DOCX
    print(f"Pasta do Excel: {excel_path}")  # Exibe o caminho onde o Excel será salvo

    # Verifica se é possível escrever na pasta de destino
    if not os.access(os.path.dirname(excel_path), os.W_OK):
        raise PermissionError(f"Não é possível gravar na pasta: {os.path.dirname(excel_path)}")

    # Abre o documento DOCX
    doc = Document(docx_path)  

    # Dicionário para armazenar tabelas organizadas por cabeçalho
    tables_by_header = {}  

    # Itera sobre todas as tabelas do documento DOCX
    for table_num, table in enumerate(doc.tables):

        # Extrai o texto das células da tabela
        data = [[cell.text for cell in row.cells] for row in table.rows]  
        
        # Verifica se a tabela é válida
        if data and len(data) > 1 and data[0]:

            # Padroniza o cabeçalho da tabela
            header = dsa_padroniza_header(data[0])  
            header_tuple = tuple(header)
            
            # Verifica se o cabeçalho é válido
            if any(header):

                # Cria um DataFrame com os dados da tabela
                df = pd.DataFrame(data[1:], columns=header)  

                # Verifica colunas duplicadas
                df.columns = dsa_verifica_coluna_unica(list(df.columns))  

                # Exibe os títulos das colunas
                print(f"Tabela {table_num + 1} títulos das colunas: {header}")  
                
                # Concatena a tabela com outras tabelas do mesmo cabeçalho
                if header_tuple in tables_by_header:
                    df = dsa_limpa_alinha_tabela(df, tables_by_header[header_tuple])
                    tables_by_header[header_tuple] = pd.concat([tables_by_header[header_tuple], df], ignore_index=True)
                else:
                    tables_by_header[header_tuple] = df
            else:
                print(f"Pular uma tabela devido a cabeçalho inválido ou vazio.")
        else:
            print(f"Pular uma tabela devido a dados ausentes ou inválidos.")

    # Verifica se há tabelas extraídas
    if tables_by_header:
        
        try:
            
            # Salva as tabelas extraídas em um arquivo Excel
            with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
                for i, (header_tuple, combined_table) in enumerate(tables_by_header.items()):
                    combined_table.columns = dsa_verifica_coluna_unica(list(combined_table.columns))
                    combined_table = dsa_remove_linhas_branco(combined_table)
                    sheet_name = f"Tabela_{i+1}"
                    combined_table.to_excel(writer, sheet_name=sheet_name, index=False)
            messagebox.showinfo("Sucesso", f"As tabelas foram extraídas e salvas com sucesso em {excel_path}")
        except Exception as e:
            print(f"Falha ao salvar o arquivo Excel: {e}")
            messagebox.showerror("Erro", f"Falha ao salvar o arquivo Excel: {e}")
    else:
        messagebox.showinfo("Nenhuma Tabela Encontrada", "Não há tabela no arquivo DOCX.")

# Função para selecionar o arquivo PDF ou DOCX
def dsa_seleciona_arquivo():
    
    file_path = filedialog.askopenfilename(title="Selecione o Arquivo", filetypes=[("PDF Files", "*.pdf"), ("Word Files", "*.docx")])
    
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

# Função para selecionar o local para salvar o arquivo Excel
def dsa_seleciona_local_salvar_excel():
    
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", title="Salvar Arquivo Excel", filetypes=[("Excel Files", "*.xlsx")])
    
    if file_path:
        excel_entry.delete(0, tk.END)
        excel_entry.insert(0, file_path)

# Função que inicia o processo de conversão com base no tipo de arquivo selecionado
def dsa_inicia_conversao():
    
    file_path = file_entry.get()
    excel_path = excel_entry.get()

    # Verifica se o caminho do arquivo e o local de salvamento estão definidos
    if not file_path or not excel_path:
        messagebox.showwarning("Entrada necessária", "Selecione o arquivo e o destino para salvar o arquivo Excel.")
    else:
        # Verifica se o arquivo é um PDF ou DOCX e chama a função de conversão correspondente
        if file_path.endswith(".pdf"):
            dsa_converte_pdf_excel(file_path, excel_path)
        elif file_path.endswith(".docx"):
            dsa_converte_docx_excel(file_path, excel_path)
        else:
            messagebox.showerror("Erro", "Tipo de arquivo não suportado. Selecione um arquivo PDF ou DOCX.")

# Configurações da interface gráfica
root = tk.Tk()
root.title("DSA - Projeto 6")

# Configuração dos componentes da interface gráfica
tk.Label(root, text="Selecione o Arquivo (PDF ou DOCX):").grid(row=0, column=0, padx=10, pady=10)
file_entry = tk.Entry(root, width=50)
file_entry.grid(row=0, column=1, padx=10, pady=10)

# Cria o botão
file_button = ttk.Button(root, text="Browse", command=dsa_seleciona_arquivo)
file_button.grid(row=0, column=2, padx=10, pady=10)

tk.Label(root, text="Selecione o Destino Para Salvar o Excel:").grid(row=1, column=0, padx=10, pady=10)
excel_entry = tk.Entry(root, width=50)
excel_entry.grid(row=1, column=1, padx=10, pady=10)

# Cria o botão
excel_button = ttk.Button(root, text="Browse", command=dsa_seleciona_local_salvar_excel)
excel_button.grid(row=1, column=2, padx=10, pady=10)

# Cria o botão
convert_button = ttk.Button(root, text="Extrair Tabela", command=dsa_inicia_conversao)
convert_button.grid(row=2, columnspan=3, pady=20)

# Inicia o loop principal da interface gráfica
root.mainloop()

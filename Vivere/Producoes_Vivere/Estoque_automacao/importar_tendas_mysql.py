import pandas as pd
import mysql.connector
import re

# Configuração do banco
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "NovaSenhaSegura123",
    "database": "vivere_estoque"
}

# Caminho do Excel
CAMINHO_XLSX = "Tendas.xlsx"

def ler_tendas_excel(caminho_excel):
    """Lê o Excel de tendas e retorna uma lista de dicts compatível com estruturas.py"""
    df = pd.read_excel(caminho_excel)

    # Normalizar nomes das colunas
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.replace('\n','')
    df.columns = df.columns.str.lower()

    estruturas = []

    # Detectar colunas que começam com 'tenda'
    tenda_cols = [col for col in df.columns if col.startswith('tenda')]

    for col in tenda_cols:
        # Extrair o número da tenda do nome da coluna
        match = re.search(r'(\d+)', col)
        if match:
            tenda_id = int(match.group(1))
        else:
            tenda_id = None

        nome_estrutura = col.upper()  # ex: 'TENDA 3X3'
        tipo = "TENDA"

        # Próxima coluna (quantidade)
        col_index = df.columns.get_loc(col)
        quantidade_col = df.columns[col_index + 1] if col_index + 1 < len(df.columns) else None

        # Iterar pelas linhas
        for idx, row in df.iterrows():
            item = row[col]

            # Ignorar linhas vazias ou cabeçalhos
            if pd.isna(item) or str(item).strip().upper() == 'MATERIAL':
                continue

            qtd = 0
            if quantidade_col and not pd.isna(row[quantidade_col]):
                try:
                    qtd = int(row[quantidade_col])
                except:
                    qtd = 0

            estruturas.append({
                "nome": nome_estrutura.title(),
                "tipo": tipo,
                "item": str(item).strip(),
                "quantidade": qtd
            })

    return estruturas


# Ler as estruturas das tendas
estruturas_tendas = ler_tendas_excel(CAMINHO_XLSX)

# Conectar ao MySQL
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

# Criar tabela de estruturas se não existir
cursor.execute("""
CREATE TABLE IF NOT EXISTS estruturas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    tipo VARCHAR(50),
    item VARCHAR(255),
    quantidade INT
)
""")

# Inserir estruturas de tendas no banco
for e in estruturas_tendas:
    cursor.execute(
        "INSERT INTO estruturas (nome, tipo, item, quantidade) VALUES (%s, %s, %s, %s)",
        (e['nome'], e['tipo'], e['item'], e['quantidade'])
    )

conn.commit()
cursor.close()
conn.close()

print("Importação de tendas para estruturas concluída com sucesso!")

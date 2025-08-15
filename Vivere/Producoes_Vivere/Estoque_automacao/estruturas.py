import pandas as pd
import re

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

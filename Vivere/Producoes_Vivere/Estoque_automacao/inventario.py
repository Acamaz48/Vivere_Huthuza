import pandas as pd
import os

# Nome do arquivo Excel na mesma pasta do script
arquivo_excel = "estoque_completo_vivere.xlsx"

if not os.path.exists(arquivo_excel):
    print(f"❌ Arquivo {arquivo_excel} não encontrado na pasta atual!")
else:
    # Ler colunas A, B, C, D: Categoria, Material, Quantidade, Observações
    df = pd.read_excel(
        arquivo_excel,
        usecols="A:D",
        names=["categoria", "material", "quantidade", "observacoes"],
        skiprows=0  # Ajuste caso precise pular linhas de cabeçalho no arquivo
    )

    # Remover linhas que não têm material ou quantidade (considerando quantidade >=0)
    df = df.dropna(subset=["material", "quantidade"])

    # Converter quantidade para numérico, erros virarão 0
    df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce").fillna(0).astype(int)

    # Opcional: remover espaços em branco nas strings
    df["categoria"] = df["categoria"].astype(str).str.strip()
    df["material"] = df["material"].astype(str).str.strip()
    df["observacoes"] = df["observacoes"].astype(str).str.strip()

    # Exportar para CSV
    df.to_csv("inventario_vivere.csv", index=False, encoding="utf-8")

    print("✅ Conversão concluída. Arquivo inventario_vivere.csv criado.")

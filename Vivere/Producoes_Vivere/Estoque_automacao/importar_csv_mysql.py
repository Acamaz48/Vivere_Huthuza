import pandas as pd
import mysql.connector

config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'NovaSenhaSegura123',
    'database': 'vivere_estoque',
    'raise_on_warnings': True
}

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    # Limpa dados antigos da tabela inventario
    cursor.execute("DELETE FROM inventario")
    conn.commit()

    # Lê o CSV completo com categoria, material, quantidade e observações
    df = pd.read_csv('inventario_vivere.csv')

    for idx, row in df.iterrows():
        categoria = str(row['categoria']).strip()
        material = str(row['material']).strip()
        try:
            quantidade = int(row['quantidade'])
        except:
            quantidade = 0
        observacoes = str(row.get('observacoes', '')).strip()  # pega a coluna observacoes, se existir

        cursor.execute("""
            INSERT INTO inventario (categoria, material, quantidade, observacoes)
            VALUES (%s, %s, %s, %s)
        """, (categoria, material, quantidade, observacoes))

    conn.commit()
    print("✅ Inventário atualizado com dados do CSV (incluindo observações)!")

except Exception as e:
    print(f"❌ Erro: {e}")

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals() and conn.is_connected():
        conn.close()

import mysql.connector
from datetime import datetime
from tabulate import tabulate
from estruturas import ler_tendas_excel

CAMINHO_TENDAS_XLSX = "Tendas.xlsx"

class EstoqueService:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='NovaSenhaSegura123',
            database='vivere_estoque'
        )
        self.carregar_tendas()

    # ----------------------------- CARREGAR TENDAS -----------------------------
    def carregar_tendas(self):
        tendas = ler_tendas_excel(CAMINHO_TENDAS_XLSX)
        cursor = self.conn.cursor()
        try:
            for t in tendas:
                cursor.execute(
                    "SELECT COUNT(*) FROM inventario WHERE material=%s AND categoria=%s",
                    (t['item'], t['nome'])
                )
                if cursor.fetchone()[0] == 0:
                    cursor.execute(
                        "INSERT INTO inventario (material, categoria, quantidade) VALUES (%s, %s, %s)",
                        (t['item'], t['nome'], t['quantidade'])
                    )
            self.conn.commit()
        finally:
            cursor.close()

    # ----------------------------- REGISTRAR MOVIMENTO -----------------------------
    def registrar_movimento(self, nome_material, tipo, quantidade):
        equipamento = self.buscar_equipamento(nome_material)
        if not equipamento:
            raise ValueError("Equipamento não encontrado.")

        quantidade = int(quantidade)
        if tipo not in ["entrada", "saida"]:
            raise ValueError("Tipo inválido. Use 'entrada' ou 'saida'.")

        if tipo == "saida" and equipamento['quantidade'] < quantidade:
            raise ValueError("Quantidade insuficiente para saída.")

        nova_quantidade = (
            equipamento['quantidade'] + quantidade
            if tipo == "entrada"
            else equipamento['quantidade'] - quantidade
        )

        cursor_update = self.conn.cursor()
        cursor_insert = self.conn.cursor()
        try:
            # Atualiza inventário
            cursor_update.execute(
                "UPDATE inventario SET quantidade=%s WHERE material=%s",
                (nova_quantidade, nome_material)
            )
            # Insere movimento
            horario = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor_insert.execute(
                "INSERT INTO movimentos (material, tipo, quantidade, horario) VALUES (%s,%s,%s,%s)",
                (nome_material, tipo, quantidade, horario)
            )
            self.conn.commit()
        finally:
            cursor_update.close()
            cursor_insert.close()

    # ----------------------------- MOSTRAR DISPONÍVEIS -----------------------------
    def mostrar_disponiveis(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "SELECT material, categoria, quantidade FROM inventario WHERE quantidade>0 AND NOT categoria LIKE 'TENDA%'"
            )
            dados = cursor.fetchall()
            if not dados:
                print("Nenhum material disponível.")
                return
            print(tabulate(dados, headers=["Material", "Categoria", "Quantidade"], tablefmt="fancy_grid", stralign="center"))
        finally:
            cursor.close()

    # ----------------------------- LISTAR MOVIMENTAÇÕES -----------------------------
    def listar_movimentacoes(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT material, tipo, quantidade, horario FROM movimentos")
            dados = cursor.fetchall()
            if not dados:
                print("Nenhuma movimentação registrada.")
                return
            print(tabulate(dados, headers=["Material", "Tipo", "Quantidade", "Horário"], tablefmt="fancy_grid", stralign="center"))
        finally:
            cursor.close()

    # ----------------------------- ADICIONAR/REMOVER EQUIPAMENTO -----------------------------
    def adicionar_equipamento(self, nome_material, quantidade, categoria=""):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM inventario WHERE material=%s", (nome_material,))
            if cursor.fetchone()[0] > 0:
                raise ValueError("Equipamento já existe.")
            cursor.execute(
                "INSERT INTO inventario (material, categoria, quantidade) VALUES (%s,%s,%s)",
                (nome_material, categoria, quantidade)
            )
            self.conn.commit()
        finally:
            cursor.close()

    def remover_equipamento(self, nome_material):
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM inventario WHERE material=%s", (nome_material,))
            self.conn.commit()
        finally:
            cursor.close()

    # ----------------------------- BUSCAR EQUIPAMENTO -----------------------------
    def buscar_equipamento(self, nome_material):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT material, quantidade FROM inventario WHERE material=%s", (nome_material,))
            row = cursor.fetchone()
            return {"nome": row[0], "quantidade": row[1]} if row else None
        finally:
            cursor.close()

    # ----------------------------- LISTAR POR CATEGORIA -----------------------------
    def listar_por_categoria(self, nome_categoria):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "SELECT material, quantidade FROM inventario WHERE categoria=%s",
                (nome_categoria,)
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def listar_categorias(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT DISTINCT categoria FROM inventario")
            return [row[0] for row in cursor.fetchall()]
        finally:
            cursor.close()

    # ----------------------------- LIMPAR E CALCULAR -----------------------------
    def limpar_estoque(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM inventario")
            cursor.execute("DELETE FROM movimentos")
            self.conn.commit()
        finally:
            cursor.close()

    def calcular_total_estoque(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT SUM(quantidade) FROM inventario")
            total = cursor.fetchone()[0]
            return total or 0
        finally:
            cursor.close()

    def calcular_total_movimentos(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM movimentos")
            total = cursor.fetchone()[0]
            return total or 0
        finally:
            cursor.close()

    # ----------------------------- REGISTRAR MOVIMENTO DE TENDA -----------------------------
    def registrar_movimento_tenda(self):
        """Fluxo amigável para editar materiais de uma tenda e registrar a tenda como um todo"""
        categorias = [c for c in self.listar_categorias() if c.upper().startswith("TENDA")]
        if not categorias:
            print("Não há tendas cadastradas.")
            return

        print("\nTendas disponíveis:")
        for i, t in enumerate(categorias, 1):
            print(f"{i}. {t}")
        try:
            escolha = int(input("Escolha a tenda: ")) - 1
            tenda_selecionada = categorias[escolha]
        except (ValueError, IndexError):
            print("Tenda inválida.")
            return

        materiais = self.listar_por_categoria(tenda_selecionada)
        print(f"\nMateriais da {tenda_selecionada}:")
        for i, (mat, qtd) in enumerate(materiais, 1):
            print(f"{i}. {mat} - {qtd}")

        # Alterar quantidades se necessário
        alterar = input("\nDeseja alterar quantidades de algum material? (s/n): ").lower()
        if alterar == 's':
            cursor = self.conn.cursor()
            try:
                for mat, qtd in materiais:
                    nova_qtd = input(f"{mat} (atual {qtd}): nova quantidade ou enter para manter: ")
                    if nova_qtd.strip():
                        cursor.execute("UPDATE inventario SET quantidade=%s WHERE material=%s", (int(nova_qtd), mat))
                self.conn.commit()
            finally:
                cursor.close()

        # Escolher tipo de movimentação
        tipo = input("Tipo de movimentação da tenda (entrada/saida): ").strip().lower()
        if tipo not in ("entrada", "saida"):
            print("Tipo inválido, usando 'saida' por padrão.")
            tipo = "saida"

        # Registrar a tenda como um todo
        confirmar = input(f"\nConfirmar movimentação da tenda {tenda_selecionada}? (s/n): ").lower()
        if confirmar != 's':
            print("Operação cancelada.")
            return

        cursor = self.conn.cursor()
        try:
            horario = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO movimentos (material, tipo, quantidade, horario) VALUES (%s,%s,%s,%s)",
                (tenda_selecionada, tipo, 1, horario)
            )
            self.conn.commit()
        finally:
            cursor.close()

        print(f"Movimentação da tenda '{tenda_selecionada}' registrada com sucesso.")

    def __del__(self):
        if self.conn.is_connected():
            self.conn.close()

import mysql.connector

class Equipamento:
    def __init__(self, id, nome, quantidade, id_categoria=None, observacoes=None):
        self.id = id
        self.nome = nome
        self.quantidade = quantidade
        self.id_categoria = id_categoria
        self.observacoes = observacoes

    def __str__(self):
        return f"Equipamento(id={self.id}, nome='{self.nome}', quantidade={self.quantidade})"

    def __repr__(self):
        return self.__str__()

    def adicionar_quantidade(self, quantidade_adicional):
        if quantidade_adicional < 0:
            raise ValueError("A quantidade adicional não pode ser negativa.")
        self.quantidade += quantidade_adicional
        return self.quantidade

    def remover_quantidade(self, quantidade_removida):
        if quantidade_removida < 0:
            raise ValueError("A quantidade removida não pode ser negativa.")
        if quantidade_removida > self.quantidade:
            raise ValueError("Não é possível remover mais do que a quantidade disponível.")
        self.quantidade -= quantidade_removida
        return self.quantidade

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "quantidade": self.quantidade,
            "id_categoria": self.id_categoria,
            "observacoes": self.observacoes
        }

    @staticmethod
    def from_db_row(row):
        # Espera-se row: (id, nome, quantidade, id_categoria, observacoes)
        return Equipamento(
            id=row[0],
            nome=row[1],
            quantidade=row[2],
            id_categoria=row[3],
            observacoes=row[4]
        )

    @staticmethod
    def buscar_por_id(conn, id_equipamento):
        cursor = conn.cursor()
        query = "SELECT id, nome, quantidade, id_categoria, observacoes FROM materiais WHERE id = %s"
        cursor.execute(query, (id_equipamento,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return Equipamento.from_db_row(row)
        else:
            raise ValueError("Equipamento não encontrado no banco.")

    def salvar_no_banco(self, conn):
        cursor = conn.cursor()
        # Verifica se equipamento já existe
        cursor.execute("SELECT COUNT(*) FROM materiais WHERE id = %s", (self.id,))
        (count,) = cursor.fetchone()
        if count == 0:
            # Inserir novo equipamento
            cursor.execute("""
                INSERT INTO materiais (id, nome, quantidade, id_categoria, observacoes)
                VALUES (%s, %s, %s, %s, %s)
            """, (self.id, self.nome, self.quantidade, self.id_categoria, self.observacoes))
        else:
            # Atualizar equipamento existente
            cursor.execute("""
                UPDATE materiais SET nome=%s, quantidade=%s, id_categoria=%s, observacoes=%s
                WHERE id=%s
            """, (self.nome, self.quantidade, self.id_categoria, self.observacoes, self.id))
        conn.commit()
        cursor.close()

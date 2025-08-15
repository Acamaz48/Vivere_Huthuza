import mysql.connector
from datetime import datetime

class Movimento:
    def __init__(self, id_equipamento, tipo, quantidade):
        self.id_equipamento = id_equipamento
        self.tipo = tipo
        self.quantidade = quantidade
        self.horario = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self):
        return (f"Movimento(id_equipamento={self.id_equipamento}, "
                f"tipo='{self.tipo}', quantidade={self.quantidade}, "
                f"horario='{self.horario}')")

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        return {
            "id_equipamento": self.id_equipamento,
            "tipo": self.tipo,
            "quantidade": self.quantidade,
            "horario": self.horario
        }

    def from_dict(self, data):
        self.id_equipamento = data.get("id_equipamento")
        self.tipo = data.get("tipo")
        self.quantidade = data.get("quantidade")
        self.horario = data.get("horario", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return self

    def salvar_no_banco(self, conexao):
        cursor = conexao.cursor()
        cursor.execute("""
            INSERT INTO movimentos (id_equipamento, tipo, quantidade, horario)
            VALUES (%s, %s, %s, %s)
        """, (self.id_equipamento, self.tipo, self.quantidade, self.horario))
        conexao.commit()
        cursor.close()

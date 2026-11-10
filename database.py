import sqlite3

def conectar():
    conexion = sqlite3.connect("parking.db")
    return conexion


def crear_tablas():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT NOT NULL,
            tipo TEXT NOT NULL,
            hora_entrada TEXT NOT NULL,
            hora_salida TEXT,
            costo REAL DEFAULT 0,
            estado TEXT DEFAULT 'Dentro'
        )
    """)

    conexion.commit()
    conexion.close()


if __name__ == "__main__":
    crear_tablas()
    print("Base de datos creada correctamente.")
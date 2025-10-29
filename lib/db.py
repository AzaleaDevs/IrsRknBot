import os
import aiosqlite

# Ruta por defecto (la puedes sobreescribir con la variable de entorno DB_PATH)
DEFAULT_DB_PATH = os.environ.get("DB_PATH", "/app/data/facturas.db")

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS FACTURAS (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    CAMPO TEXT NOT NULL,
    MES INTEGER NOT NULL CHECK (MES BETWEEN 1 AND 12),
    ANYO INTEGER NOT NULL CHECK (ANYO >= 2000),
    IMPORTE REAL NOT NULL CHECK (IMPORTE >= 0)
);
"""

async def init_db(db_path: str = DEFAULT_DB_PATH):
    """Inicializa la base de datos y crea las tablas si no existen."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    async with aiosqlite.connect(db_path) as db:
        await db.executescript(SCHEMA_SQL)
        await db.commit()
        print(f"🗄️ Base de datos inicializada en {db_path}")

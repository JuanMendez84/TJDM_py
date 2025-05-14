import sqlite3

DB_PATH = "miapp.db"

def crear_tabla_juegos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS JUEGOS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Nombre TEXT NOT NULL,
            MinJugadores INTEGER NOT NULL,
            MaxJugadores INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def crear_bd():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS USUARIOS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            contrasena TEXT NOT NULL,
            nombre TEXT
        )
    ''')
    cursor.execute(
        "INSERT OR IGNORE INTO USUARIOS (usuario, contrasena) VALUES (?, ?)",
        ("admin", "1234")
    )
    conn.commit()
    conn.close()

def crear_tabla_categorias():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CATEGORIAS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def verificar_credenciales(usuario, contrasena):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM USUARIOS WHERE usuario=? AND contrasena=?",
        (usuario, contrasena)
    )
    resultado = cursor.fetchone()
    conn.close()
    return resultado is not None

def crear_tabla_juegos_categorias():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS JUEGOS_CATEGORIAS (
            juego_id INTEGER NOT NULL,
            categoria_id INTEGER NOT NULL,
            PRIMARY KEY (juego_id, categoria_id),
            FOREIGN KEY (juego_id) REFERENCES JUEGOS(id) ON DELETE CASCADE,
            FOREIGN KEY (categoria_id) REFERENCES CATEGORIAS(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()

def obtener_categorias_de_juego(juego_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT C.nombre
        FROM CATEGORIAS C
        JOIN JUEGOS_CATEGORIAS JC ON C.id = JC.categoria_id
        WHERE JC.juego_id = ?
        ORDER BY C.nombre
    ''', (juego_id,))
    categorias = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categorias

def crear_tablas_torneos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabla principal TORNEOS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TORNEOS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            descripcion TEXT,
            fecha_creacion TEXT NOT NULL,
            fecha_inicio TEXT NOT NULL,
            fecha_fin TEXT
        )
    ''')
    
    # Tabla intermedia TORNEOS_USUARIOS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TORNEOS_USUARIOS (
            torneo_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            PRIMARY KEY (torneo_id, usuario_id),
            FOREIGN KEY (torneo_id) REFERENCES TORNEOS(id) ON DELETE CASCADE,
            FOREIGN KEY (usuario_id) REFERENCES USUARIOS(id) ON DELETE CASCADE
        )
    ''')
    
    # Tabla intermedia TORNEOS_JUEGOS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TORNEOS_JUEGOS (
            torneo_id INTEGER NOT NULL,
            juego_id INTEGER NOT NULL,
            PRIMARY KEY (torneo_id, juego_id),
            FOREIGN KEY (torneo_id) REFERENCES TORNEOS(id) ON DELETE CASCADE,
            FOREIGN KEY (juego_id) REFERENCES JUEGOS(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

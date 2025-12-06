import sqlite3

conn = sqlite3.connect("labels.db")
cursor = conn.cursor()

# ================== USERS ==================
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

# ================== MASTERS ==================
cursor.execute("""
CREATE TABLE IF NOT EXISTS masters(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mawb_number TEXT NOT NULL,
    origin TEXT NOT NULL,
    destination TEXT NOT NULL,
    service TEXT NOT NULL,
    total_pieces INTEGER NOT NULL,
    created_by TEXT,
    label_size TEXT DEFAULT '4x6',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ================== HOUSES ==================
cursor.execute("""
CREATE TABLE IF NOT EXISTS houses(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    master_id INTEGER,
    hawb_number TEXT NOT NULL,
    pieces INTEGER NOT NULL,
    FOREIGN KEY (master_id) REFERENCES masters(id)
)
""")

# ================== LABELS ==================
cursor.execute("""
CREATE TABLE IF NOT EXISTS labels(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    master_id INTEGER,
    house_id INTEGER,
    mawb_counter TEXT,
    hawb_counter TEXT,
    barcode_data TEXT,
    FOREIGN KEY (master_id) REFERENCES masters(id),
    FOREIGN KEY (house_id) REFERENCES houses(id)
)
""")

# ================== LOGS (BITÁCORA) ==================
cursor.execute("""
CREATE TABLE IF NOT EXISTS logs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT NOT NULL,
    action TEXT NOT NULL,
    mawb_number TEXT,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ================== CORRECCIÓN PARA BD VIEJA (EXITENTE) ==================
# Por si la tabla masters ya existe sin la columna label_size
cursor.execute("PRAGMA table_info(masters)")
columns = [col[1] for col in cursor.fetchall()]

if "label_size" not in columns:
    cursor.execute("ALTER TABLE masters ADD COLUMN label_size TEXT DEFAULT '4x6'")
    print("✅ Columna label_size agregada a masters")
else:
    print("✅ La columna label_size ya existe")

# ================== USUARIO ADMIN ==================
cursor.execute("""
INSERT OR IGNORE INTO users (username, password, role)
VALUES ('admin', '1234', 'admin')
""")

conn.commit()
conn.close()

print("✅ Base de datos creada / actualizada correctamente")

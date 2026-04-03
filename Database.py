import sqlite3


# ===================== CONNECTION =====================

def get_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# ===================== INIT DATABASE =====================

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # ===================== CATEGORIES =====================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    """)

    # ===================== PRODUCTS =====================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_code TEXT,
        name TEXT NOT NULL,
        price INTEGER,
        stock INTEGER,
        sold INTEGER DEFAULT 0,
        product_type TEXT,
        category_id INTEGER,
        description TEXT,
        image TEXT,
        real_price INTEGER DEFAULT 0,
        admin_notes TEXT DEFAULT '',
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )
    """)

    # ===================== CATALOG GUIDES =====================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS catalog_guides (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand TEXT NOT NULL,
        pk TEXT NOT NULL,
        pdf_file TEXT NOT NULL
    )
    """)

# ===================== MIGRATION: tambah kolom baru jika belum ada =====================
    existing_columns = [row[1] for row in cursor.execute("PRAGMA table_info(products)").fetchall()]

    if 'real_price' not in existing_columns:
        cursor.execute("ALTER TABLE products ADD COLUMN real_price INTEGER DEFAULT 0")
        print("[MIGRATION] Kolom real_price ditambahkan.")

    if 'admin_notes' not in existing_columns:
        cursor.execute("ALTER TABLE products ADD COLUMN admin_notes TEXT DEFAULT ''")
        print("[MIGRATION] Kolom admin_notes ditambahkan.")

    # Add logo_url to categories if missing
    cat_columns = [row[1] for row in cursor.execute("PRAGMA table_info(categories)").fetchall()]
    if 'logo_url' not in cat_columns:
        cursor.execute("ALTER TABLE categories ADD COLUMN logo_url TEXT DEFAULT ''")
        print("[MIGRATION] Kolom logo_url ditambahkan ke categories.")

    # ===================== SEED CATEGORIES =====================
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO categories (name, logo_url) VALUES (?, ?)
        """, [
            ("Parsun", '/static/images/parsun.png'),
            ("Yamaha Marine", '/static/images/yamaha.png'),
            ("Mercury Marine", '/static/images/mercury.png'),
            ("Suzuki Marine", '/static/images/suzuki.png'),
            ("Honda Marine", '/static/images/honda.png'),
            ("Omax Marine", '/static/images/omax.png'),
        ])

    # ===================== SEED CATALOG GUIDES =====================
    cursor.execute("SELECT COUNT(*) FROM catalog_guides")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO catalog_guides (brand, pk, pdf_file) VALUES (?, ?, ?)
        """, [
            ("Yamaha Marine", "15PK", "yamaha_15pk.pdf"),
            ("Yamaha Marine", "30PK", "yamaha_30pk.pdf"),
            ("Parsun", "15PK", "parsun_15pk.pdf"),
            ("Parsun", "30PK", "parsun_30pk.pdf")
        ])

    conn.commit()
    conn.close()
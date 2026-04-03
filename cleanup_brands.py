from Database import get_connection, init_db

init_db()
conn = get_connection()
cursor = conn.cursor()

# Hapus products Suzuki & Honda
cursor.execute("SELECT id FROM categories WHERE name IN ('Suzuki Marine', 'Honda Marine')")
cat_ids = [row['id'] for row in cursor.fetchall()]
print(f"Suzuki/Honda category IDs: {cat_ids}")

if cat_ids:
    cursor.execute("DELETE FROM products WHERE category_id IN ({})".format(','.join('?' * len(cat_ids))), cat_ids)
    print(f"Deleted {cursor.rowcount} products")

# Hapus categories
cursor.execute("DELETE FROM categories WHERE name IN ('Suzuki Marine', 'Honda Marine')")
print(f"Deleted {cursor.rowcount} categories")

# Tambah Vini
# cursor.execute("INSERT OR IGNORE INTO categories (name, logo_url) VALUES (?, ?)", ("Vini", '/static/images/vini.png'))
# print("Added Vini category (ignore if exists)")

conn.commit()
conn.close()
print("Done. Run python check_db.py to verify.")

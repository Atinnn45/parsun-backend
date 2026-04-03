from Database import get_connection

print("=== DATABASE PARSUN BATAM ===")

conn = get_connection()
cursor = conn.cursor()

# Total produk
cursor.execute("SELECT COUNT(*) FROM products")
total = cursor.fetchone()[0]
print(f"📦 Total Produk: {total}")

# Total kategori
cursor.execute("SELECT COUNT(*) FROM categories")
cats = cursor.fetchone()[0]
print(f"🏷️  Total Kategori: {cats}")

# Produk terbaru 10
print("\n📋 10 PRODUK TERBARU:")
cursor.execute("""
    SELECT p.id, p.product_code, p.name, p.stock, p.price, c.name as category
    FROM products p 
    JOIN categories c ON p.category_id = c.id 
    ORDER BY p.id DESC LIMIT 10
""")
for row in cursor.fetchall():
    print(f"  ID:{row[0]:3} | {row[1]:10} | {row[2][:40]:40} | Stok:{row[3]:2} | Rp{row[4]:,}")

# Stok habis
print("\n⚠️  PRODUK HABIS (stok=0):")
cursor.execute("SELECT COUNT(*) FROM products WHERE stock <= 0")
print(f"  {cursor.fetchone()[0]} produk INDENT")

conn.close()
print("\n✅ Database siap! Run: python check_db.py kapan saja.")


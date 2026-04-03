from Database import get_connection, init_db

# Daftar kategori bawaan
default_categories = [
    "Parsun",
    "Yamaha Marine",
    "Mercury Marine",
    "Suzuki Marine",
    "Honda Marine",
    "Omax Marine",
]

# Jalankan
init_db()
conn = get_connection()
cursor = conn.cursor()

for name in default_categories:
    cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))

conn.commit()
conn.close()

print("Kategori berhasil ditambahkan!")

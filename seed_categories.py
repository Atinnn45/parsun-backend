from Database import get_connection, init_db

init_db()
conn = get_connection()
cursor = conn.cursor()

logos = {
    "Parsun": "/static/images/Parsun.png",
    "Mercury Marine": "/static/images/mercury.png",
    "Yamaha Marine": "/static/images/yamaha.png",
    "Suzuki Marine": "/static/images/suzuki.png",
    "Honda Marine": "/static/images/honda.png",
    "Omax Marine": "/static/images/omax.png"
    
}

updated = 0
for name, logo in logos.items():
    cursor.execute("UPDATE categories SET logo_url = ? WHERE name = ?", (logo, name))
    if cursor.rowcount > 0:
        updated += 1
        print(f"Updated {name}: {logo}")

conn.commit()
conn.close()
print(f"Updated {updated}/6 categories.")

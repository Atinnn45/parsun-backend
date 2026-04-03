from Database import get_connection

conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT id, name, logo_url FROM categories")
cats = cursor.fetchall()
print("Categories:")
for cat in cats:
    print(f"ID: {cat['id']} | Name: {cat['name']} | Logo: '{cat['logo_url']}'")
conn.close()

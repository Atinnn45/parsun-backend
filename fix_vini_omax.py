from Database import get_connection

conn = get_connection()
cursor = conn.cursor()

# Fix Omax logo
cursor.execute("UPDATE categories SET logo_url = '/static/images/omax.png' WHERE name = 'Omax Marine'")
print("Omax updated: {} rows".format(cursor.rowcount))

# Delete duplicate Vini (ID 8, keep ID 7)
cursor.execute("DELETE FROM categories WHERE id = 8")
print("Deleted duplicate Vini ID 8")

# Fix Vini logo to empty (no vini.png file)
cursor.execute("UPDATE categories SET logo_url = '' WHERE id = 7")
print("Vini logo set to empty")

conn.commit()
conn.close()
print("\n✅ Fixed! Run: python db_check.py to verify.")

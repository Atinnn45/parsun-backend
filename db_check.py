from Database import get_connection
conn = get_connection()
cursor = conn.cursor()
print("=== CATEGORIES ===")
cursor.execute("SELECT id, name, logo_url FROM categories ORDER BY name")
for row in cursor.fetchall():
    logo = row[2] or "NONE"
    print(f"ID:{row[0]:2} | {row[1]:20} | {logo}")
print("\n=== DUPLICATES ===")
cursor.execute("""
    SELECT name, COUNT(*) as count 
    FROM categories 
    GROUP BY name 
    HAVING count > 1
""")
dups = cursor.fetchall()
if dups:
    for row in dups:
        print(f"DUPLICATE: {row[0]} ({row[1]} times)")
else:
    print("No duplicates")
print("\n=== OMAX CHECK ===")
cursor.execute("SELECT * FROM categories WHERE name LIKE '%omax%' OR name LIKE '%Omax%'")
omax = cursor.fetchone()
if omax:
    print(f"Omax: ID={omax[0]}, name='{omax[1]}', logo='{omax[2] or 'NONE'}'")
else:
    print("No Omax found")
conn.close()


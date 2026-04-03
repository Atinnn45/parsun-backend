import sqlite3
conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute("UPDATE categories SET logo_url = '/static/images/yamaha.png' WHERE id=2")
c.execute("UPDATE categories SET logo_url = '/static/images/omax.png' WHERE name='Omax Marine'")
conn.commit()
print('Updated logos to PNG!')
for row in c.execute('SELECT * FROM categories'):
    print(dict(row))
conn.close()

# init_db.py
import sqlite3

conn = sqlite3.connect('app/database.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
''')

# Insert some users if empty
c.execute('SELECT COUNT(*) FROM users')
if c.fetchone()[0] == 0:
    c.executemany('INSERT INTO users (name) VALUES (?)', [('Amit',), ('Arjun',), ('Arvind',)])

conn.commit()
conn.close()

print("Database initialized with users table.")

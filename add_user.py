# add_users.py
import sqlite3

conn = sqlite3.connect('app/database.db')
c = conn.cursor()

# Add new users
new_users = [('Amit',), ('Sumit',), ('Raju',)]
c.executemany('INSERT INTO users (name) VALUES (?)', new_users)

conn.commit()
conn.close()

print("Users added successfully.")

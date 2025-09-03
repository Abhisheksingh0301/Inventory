# db.py
import sqlite3
from flask import g
import os
from flask import current_app

DATABASE = 'app/database.db'  # path to your SQLite DB file

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # to access columns by name
    return db

def close_db(e=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource('app/schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
    db.commit()

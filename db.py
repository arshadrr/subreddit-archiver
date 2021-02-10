import sqlite3
import os

import config

def get_schema():
    with open(config.SCHEMA_FILE) as f:
        return f.read()

def get_connection(name):
    name += ".sqlite"

    if not os.path.exists(name):
        with sqlite3.connect(name) as conn:
            cur = conn.cursor()
            cur.executescript(get_schema())

    return sqlite3.connect(name)

def insert_posts(db_connection, posts):
    cursor = db_connection.cursor()
    cursor.executemany(
            'INSERT OR IGNORE INTO posts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
            posts
            )
    db_connection.commit()

def insert_comments(db_connection, comments):
    cursor = db_connection.cursor()
    cursor.executemany(
            'INSERT OR IGNORE INTO comments VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
            comments
            )
    db_connection.commit()

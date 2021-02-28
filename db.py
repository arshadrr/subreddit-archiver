import sqlite3
import os


SCHEMA_FILE = "schema.sql"

def get_schema():
    with open(SCHEMA_FILE) as f:
        return f.read()

def get_connection(file_name):
    if not os.path.exists(file_name):
        with sqlite3.connect(file_name) as conn:
            cur = conn.cursor()
            cur.executescript(get_schema())

    return sqlite3.connect(file_name)

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

def set_kv(db_connection, key, value):
    cursor = db_connection.cursor()
    cursor.execute('INSERT OR REPLACE INTO archive_metadata VALUES (?, ?)', (key, value))
    db_connection.commit()

def get_kv(db_connection, key):
    cursor = db_connection.cursor()
    value = cursor.execute(
            'SELECT value FROM archive_metadata WHERE key = ?',
            (key,)
            ).fetchall()
    db_connection.commit()

    if value:
        return value[0][0]
    else:
        raise KeyError

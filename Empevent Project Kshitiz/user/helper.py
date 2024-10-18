import sqlite3

DATABASE_NAME = 'Database.db'

# Helper Functions for Flask app

# Make sure the SQL query gives the column names along with the query results
def row_to_dict(cursor: sqlite3.Cursor, row: sqlite3.Row) -> dict:
    data = {}
    for idx, col in enumerate(cursor.description):
        data[col[0]] = row[idx]
    return data

# Execute SQL query in the ecommerce.db SQLite3 database
def execute_query(query):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.row_factory = row_to_dict
    
    try:
        c.execute(query)
        if query.strip().upper().startswith("SELECT"):
            results = c.fetchall()
        else:
            conn.commit()
            results = None
    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
    
    return results

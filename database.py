import sqlite3

# DB Setup
conn = sqlite3.connect("test.db", check_same_thread=False)
cursor = conn.cursor()

def setup_database():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        amount INTEGER
    )
    """)

    # Reset data (for demo)
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM orders")

    cursor.executemany("INSERT INTO users VALUES (?, ?)", [
        (1, "Rahul"),
        (2, "Anita")
    ])

    cursor.executemany("INSERT INTO orders VALUES (?, ?, ?)", [
        (1, 1, 500),
        (2, 1, 700),
        (3, 2, 300)
    ])

    conn.commit()


# Execute SQL (with validation)
def execute_sql(sql):
    try:
        # Safety check
        if not sql.lower().strip().startswith("select"):
            return "Error: Only SELECT queries are allowed."

        cursor.execute(sql)
        return cursor.fetchall()

    except Exception as e:
        return f"Error: {str(e)}"
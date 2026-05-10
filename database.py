import sqlite3

DATABASE_PATH = "database.db"

conn = sqlite3.connect(
    DATABASE_PATH,
    check_same_thread=False
)

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

    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM orders")

    cursor.executemany(
        "INSERT INTO users VALUES (?, ?)",
        [
            (1, "Rahul"),
            (2, "Anita")
        ]
    )

    cursor.executemany(
        "INSERT INTO orders VALUES (?, ?, ?)",
        [
            (1, 1, 500),
            (2, 1, 700),
            (3, 2, 300)
        ]
    )

    conn.commit()


def get_tables():

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name NOT LIKE 'sqlite_%';
    """)

    tables = cursor.fetchall()

    return [table[0] for table in tables]


def get_schema():

    schema = {}

    tables = get_tables()

    for table in tables:

        cursor.execute(
            f"PRAGMA table_info({table})"
        )

        columns = cursor.fetchall()

        schema[table] = []

        for column in columns:

            col_name = column[1]
            col_type = column[2]

            schema[table].append(
                f"{col_name} {col_type}"
            )

    return schema


def get_relationships():

    relationships = []

    tables = get_tables()

    for table in tables:

        cursor.execute(
            f"PRAGMA foreign_key_list({table})"
        )

        foreign_keys = cursor.fetchall()

        for fk in foreign_keys:

            ref_table = fk[2]
            from_col = fk[3]
            to_col = fk[4]

            relationships.append(
                f"{table}.{from_col} -> {ref_table}.{to_col}"
            )

    return relationships


def schema_to_text(schema):

    lines = []

    for table, columns in schema.items():

        cols = ", ".join(columns)

        lines.append(
            f"{table}({cols})"
        )

    return "\n".join(lines)


def relationships_to_text(relationships):

    return "\n".join(relationships)


def get_sample_data(limit=2):

    sample_text = []

    tables = get_tables()

    for table in tables:

        try:

            cursor.execute(
                f"SELECT * FROM {table} LIMIT {limit}"
            )

            rows = cursor.fetchall()

            sample_text.append(
                f"{table} sample rows: {rows}"
            )

        except:
            continue

    return "\n".join(sample_text)


def clean_sql(sql_query):

    sql_query = sql_query.strip()

    sql_query = sql_query.replace(
        "```sql",
        ""
    )

    sql_query = sql_query.replace(
        "```",
        ""
    )

    return sql_query.strip()


def validate_sql(sql_query):

    sql_lower = sql_query.lower().strip()

    blocked_keywords = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "truncate"
    ]

    for keyword in blocked_keywords:

        if keyword in sql_lower:
            return False

    return sql_lower.startswith("select")


def validate_tables_and_columns(sql_query):

    schema = get_schema()

    valid_tables = list(schema.keys())

    valid_columns = []

    for cols in schema.values():

        for col in cols:

            column_name = col.split()[0]

            valid_columns.append(column_name)

    sql_keywords = [
        "select",
        "from",
        "where",
        "join",
        "on",
        "group",
        "by",
        "order",
        "limit",
        "having",
        "and",
        "or",
        "as",
        "sum",
        "count",
        "avg",
        "min",
        "max",
        "distinct",
        "inner",
        "left",
        "right",
        "outer",
        "like",
        "in",
        "between",
        "desc",
        "asc"
    ]

    tokens = (
        sql_query
        .replace(",", " ")
        .replace("(", " ")
        .replace(")", " ")
        .split()
    )

    for token in tokens:

        token = token.strip()

        if "." in token:

            token = token.split(".")[-1]

        token_lower = token.lower()

        if (
            token_lower not in sql_keywords
            and token not in valid_tables
            and token not in valid_columns
        ):

            if token.isidentifier():

                return False

    return True


def execute_sql(sql_query):

    try:

        sql_query = clean_sql(sql_query)

        is_safe = validate_sql(sql_query)

        if not is_safe:

            return "Error: Unsafe query detected."

        is_valid_schema = validate_tables_and_columns(
            sql_query
        )

        if not is_valid_schema:

            return (
                "Error: Hallucinated table or "
                "column detected."
            )

        cursor.execute(sql_query)

        rows = cursor.fetchall()

        return rows

    except Exception as e:

        return f"Error: {str(e)}"
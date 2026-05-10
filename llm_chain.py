import sqlite3

# Database Connect
DATABASE_PATH = "database.db"

conn = sqlite3.connect(
    DATABASE_PATH,
    check_same_thread=False
)

cursor = conn.cursor()

# Fetch All Tables
def get_tables():

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name NOT LIKE 'sqlite_%';
    """)

    tables = cursor.fetchall()

    return [table[0] for table in tables]


# Fetch Schema Dynamically

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


# Fetch Foreign Key Relationships
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


# Convert Schema to Text
def schema_to_text(schema):

    lines = []

    for table, columns in schema.items():

        cols = ", ".join(columns)

        lines.append(
            f"{table}({cols})"
        )

    return "\n".join(lines)


# Convert Relationships to Text
def relationships_to_text(relationships):

    return "\n".join(relationships)


# Fetch Sample Data
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


# Clean SQL Response

def clean_sql(sql_query):

    sql_query = sql_query.strip()

    # Remove markdown blocks
    sql_query = sql_query.replace(
        "```sql",
        ""
    )

    sql_query = sql_query.replace(
        "```",
        ""
    )

    return sql_query.strip()


# SQL Safety Validation

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


# Execute SQL Query

def execute_sql(sql_query):

    try:

        # Clean SQL
        sql_query = clean_sql(sql_query)

        # Validate SQL
        is_safe = validate_sql(sql_query)

        if not is_safe:

            return "Error: Unsafe query detected."

        # Execute query
        cursor.execute(sql_query)

        rows = cursor.fetchall()

        return rows

    except Exception as e:

        return f"Error: {str(e)}"
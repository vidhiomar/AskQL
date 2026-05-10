import sqlite3
from groq import Groq
from dotenv import load_dotenv
import os

# Load env
load_dotenv()

# Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# SQLite Connection
DATABASE_PATH = "database.db"
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Fetch Tables
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

# Fetch Foreign Keys

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

# Convert Schema to Prompt Text

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

# Build Prompt
def build_prompt(question):

    schema = get_schema()

    relationships = get_relationships()

    schema_text = schema_to_text(schema)

    relationship_text = relationships_to_text(
        relationships
    )

    return f"""
You are a SQLite SQL expert.

Database Schema:
{schema_text}

Relationships:
{relationship_text}

Rules:
- Only use tables provided above
- Only use columns provided above
- Always use proper JOINs
- Only generate SELECT queries
- Do NOT generate INSERT, UPDATE, DELETE, DROP
- Return ONLY SQL query
- No explanations
- Use SQLite syntax only

User Question:
{question}
"""

#Clean SQL
def clean_sql(sql):
    sql = sql.strip()

    if "```" in sql:
        sql = sql.split("```")[-2]

    return sql.strip()

# Generate SQL
def generate_sql(question):

    prompt = build_prompt(question)

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    sql_query = response.choices[0].message.content.strip()
    sql_query = clean_sql(sql_query)
    return sql_query

# Execute SQL
def execute_sql(sql_query):
    try:
        sql_lower = sql_query.lower().strip()

        if not sql_lower.startswith("select"):
            return "Error: Only SELECT queries are allowed."

        cursor.execute(sql_query)
        rows = cursor.fetchall()
        return rows

    except Exception as e:
        return str(e)

# Fix SQL Errors
def fix_sql(previous_sql, error_msg):

    schema = get_schema()

    relationships = get_relationships()

    schema_text = schema_to_text(schema)

    relationship_text = relationships_to_text(
        relationships
    )

    fix_prompt = f"""
You are a SQLite SQL expert.

Database Schema:
{schema_text}

Relationships:
{relationship_text}

The following SQL query produced an error.

SQL:
{previous_sql}

Error:
{error_msg}

Fix the SQL query.

Rules:
- Return ONLY corrected SQL
- Only SELECT queries allowed
- Use valid SQLite syntax
- If aggregation is needed, use SUM, COUNT, AVG correctly
- Always use table aliases when joining
- Prefer explicit JOIN instead of implicit joins
- Use only existing tables and columns
- No explanations
"""

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "user",
                "content": fix_prompt
            }
        ],
        temperature=0
    )

    fixed_query = response.choices[0].message.content.strip()

    return fixed_query

# Full AI SQL Pipeline

def ask_database(question):

    print(f"\nQuestion: {question}")

    sql_query = generate_sql(question)

    print(f"\nGenerated SQL:\n{sql_query}")

    result = execute_sql(sql_query)

    # If SQL Error then Auto Fix
    if isinstance(result, str):

        print(f"\nSQL Error:\n{result}")

        fixed_sql = fix_sql(
            sql_query,
            result
        )

        print(f"\nFixed SQL:\n{fixed_sql}")

        result = execute_sql(fixed_sql)

    return result

# Usage

if __name__ == "__main__":

    question = "Show all users and their order amounts"

    result = ask_database(question)

    print("\nFinal Result:")

    for row in result:
        print(row)
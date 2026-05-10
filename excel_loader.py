import pandas as pd
import sqlite3
import re

DATABASE_PATH = "database.db"

# Clean Column Names

def clean_column_name(column):

    column = column.strip().lower()
    column = re.sub(r"\s+", "_", column)
    column = re.sub(r"[^a-zA-Z0-9_]", "", column)

    return column


# Clean Table Name

def clean_table_name(name):

    name = name.strip().lower()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^a-zA-Z0-9_]", "", name)

    return name


# Upload Excel to SQLite

def upload_excel_to_db(file_path, table_name=None):

    try:
        df = pd.read_excel(file_path)

        # Clean Column Names
        df.columns = [
            clean_column_name(col)
            for col in df.columns
        ]

        # Auto Table Name
        if table_name is None:

            table_name = file_path.split("/")[-1]
            table_name = table_name.split(".")[0]

        table_name = clean_table_name(table_name)

        # Connect SQLite
        conn = sqlite3.connect(DATABASE_PATH)

        # Store Data
        df.to_sql(
            table_name, conn, if_exists="replace", index=False
        )

        conn.close()

        return {
            "success": True,
            "table_name": table_name,
            "columns": list(df.columns),
            "rows": len(df)
        }

    except Exception as e:

        return {
            "success": False,"error": str(e)
        }
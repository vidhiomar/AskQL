import pandas as pd
import sqlite3
import re
import os

from database import clear_database

DATABASE_PATH = "database.db"


def clean_column_name(column):

    column = str(column)

    column = column.strip().lower()

    column = re.sub(
        r"\s+",
        "_",
        column
    )

    column = re.sub(
        r"[^a-zA-Z0-9_]",
        "",
        column
    )

    if (
        column == ""
        or column.startswith("unnamed")
    ):
        column = "unknown_column"

    return column


def clean_table_name(name):

    name = str(name)

    name = name.strip().lower()

    name = re.sub(
        r"\s+",
        "_",
        name
    )

    name = re.sub(
        r"[^a-zA-Z0-9_]",
        "",
        name
    )

    if name == "":
        name = "uploaded_table"

    return name


def load_file(file_path):

    extension = os.path.splitext(
        file_path
    )[1].lower()


    # READ RAW FILE

    if extension == ".csv":

        try:

            raw_df = pd.read_csv(
                file_path,
                encoding="utf-8",
                header=None
            )

        except:

            raw_df = pd.read_csv(
                file_path,
                encoding="latin1",
                header=None
            )

    elif extension in [".xlsx", ".xls"]:

        engine = (
            "openpyxl"
            if extension == ".xlsx"
            else "xlrd"
        )

        raw_df = pd.read_excel(
            file_path,
            engine=engine,
            header=None
        )

    else:

        raise Exception(
            f"Unsupported file format: {extension}"
        )

    # -------------------------
    # DETECT HEADER ROW
    # -------------------------

    header_row = 0

    for i in range(min(20, len(raw_df))):

        row_values = raw_df.iloc[i].astype(str)

        joined_row = " ".join(
            row_values
        ).lower()

        if any(
            keyword in joined_row
            for keyword in [
                "store",
                "date",
                "sales",
                "rent",
                "wages",
                "targetsales",
                "metric"
            ]
        ):

            header_row = i
            break

    # -------------------------
    # RELOAD USING HEADER ROW
    # -------------------------

    if extension == ".csv":

        try:

            df = pd.read_csv(
                file_path,
                encoding="utf-8",
                header=header_row
            )

        except:

            df = pd.read_csv(
                file_path,
                encoding="latin1",
                header=header_row
            )

    else:

        df = pd.read_excel(
            file_path,
            engine=engine,
            header=header_row
        )

    # -------------------------
    # CLEAN DATA
    # -------------------------

    # Remove empty rows
    df = df.dropna(
        axis=0,
        how="all"
    )

    # Remove empty columns
    df = df.dropna(
        axis=1,
        how="all"
    )

    # Remove unnamed columns
    df = df.loc[
        :,
        ~df.columns.astype(str).str.contains(
            "^Unnamed",
            case=False
        )
    ]

    return df


def upload_excel_to_db(
    file_path,
    table_name=None
):

    try:

        # Load cleaned dataframe
        df = load_file(
            file_path
        )

        # Clean column names
        cleaned_columns = []

        for idx, col in enumerate(df.columns):

            cleaned_col = clean_column_name(
                col
            )

            # Prevent duplicate columns
            if cleaned_col in cleaned_columns:

                cleaned_col = (
                    f"{cleaned_col}_{idx}"
                )

            cleaned_columns.append(
                cleaned_col
            )

        df.columns = cleaned_columns

        # Generate table name
        if table_name is None:

            table_name = (
                os.path.basename(file_path)
                .split(".")[0]
            )

        table_name = clean_table_name(
            table_name
        )

        # Connect DB
        conn = sqlite3.connect(
            DATABASE_PATH
        )

        # -------------------------
        # CLEAR OLD TABLES
        # -------------------------

        clear_database()

        # -------------------------
        # STORE NEW TABLE
        # -------------------------

        df.to_sql(
            table_name,
            conn,
            if_exists="replace",
            index=False
        )

        conn.close()

        return {
            "success": True,
            "table_name": table_name,
            "columns": list(df.columns),
            "rows": len(df)
        }

    except Exception as e:

        print("\nUPLOAD ERROR:")
        print(str(e))

        return {
            "success": False,
            "error": str(e)
        }
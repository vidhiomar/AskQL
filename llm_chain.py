from groq import Groq
from dotenv import load_dotenv
import os

from prompt import (
    sql_generation_prompt,
    sql_fix_prompt,
    explain_result_prompt
)

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Generate SQL

def generate_sql(
    question,
    schema_text,
    relationship_text,
    sample_data_text=""
):

    prompt = sql_generation_prompt(
        schema_text=schema_text,
        relationship_text=relationship_text,
        question=question,
        sample_data_text=sample_data_text
    )

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

    return sql_query

# Fix SQL Errors

def fix_sql(
    previous_sql, error_msg,schema_text,
    relationship_text,sample_data_text=""
):

    prompt = sql_fix_prompt(
        schema_text=schema_text,
        relationship_text=relationship_text,
        previous_sql=previous_sql,
        error_msg=error_msg,
        sample_data_text=sample_data_text
    )

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

    fixed_query = response.choices[0].message.content.strip()

    return fixed_query

# Explain Results

def explain_result(
    question,
    sql_query,
    result
):

    prompt = explain_result_prompt(
        question=question,
        sql_query=sql_query,
        result=result
    )

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    explanation = response.choices[0].message.content.strip()

    return explanation
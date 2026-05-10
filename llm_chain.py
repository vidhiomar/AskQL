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

MODEL_NAME = "llama-3.1-8b-instant"


def clean_llm_response(text):

    text = text.strip()

    text = text.replace(
        "```sql",
        ""
    )

    text = text.replace(
        "```",
        ""
    )

    return text.strip()


def generate_sql(
    question,
    schema_text,
    relationship_text,
    sample_data_text=""
):

    try:

        prompt = sql_generation_prompt(
            schema_text=schema_text,
            relationship_text=relationship_text,
            question=question,
            sample_data_text=sample_data_text
        )

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            max_tokens=120
        )

        sql_query = (
            response
            .choices[0]
            .message
            .content
        )

        sql_query = clean_llm_response(
            sql_query
        )

        return sql_query

    except Exception as e:

        return f"Error: {str(e)}"


def fix_sql(
    previous_sql,
    error_msg,
    schema_text,
    relationship_text,
    sample_data_text=""
):

    try:

        prompt = sql_fix_prompt(
            schema_text=schema_text,
            relationship_text=relationship_text,
            previous_sql=previous_sql,
            error_msg=error_msg,
            sample_data_text=sample_data_text
        )

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            max_tokens=300
        )

        fixed_query = (
            response
            .choices[0]
            .message
            .content
        )

        fixed_query = clean_llm_response(
            fixed_query
        )

        return fixed_query

    except Exception as e:

        return f"Error: {str(e)}"


def explain_result(
    question,
    sql_query,
    result
):

    try:

        prompt = explain_result_prompt(
            question=question,
            sql_query=sql_query,
            result=result
        )

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=200
        )

        explanation = (
            response
            .choices[0]
            .message
            .content
        )

        explanation = clean_llm_response(
            explanation
        )

        return explanation

    except Exception as e:

        return f"Explanation Error: {str(e)}"
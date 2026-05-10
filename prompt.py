# Main SQL Generation 
def sql_generation_prompt(
    schema_text,
    relationship_text,
    question,
    sample_data_text=""
):

    return f"""
You are an elite SQLite SQL expert.

Your task is to convert natural language into accurate SQL queries.

DATABASE SCHEMA
{schema_text}

TABLE RELATIONSHIPS
{relationship_text}

SAMPLE DATA
{sample_data_text}

IMPORTANT RULES

1. ONLY generate SQL SELECT queries
2. NEVER generate:
   - INSERT
   - UPDATE
   - DELETE
   - DROP
   - ALTER
   - TRUNCATE

3. ONLY use tables provided in schema
4. ONLY use columns provided in schema
5. Always use proper JOINs when required
6. Use explicit JOIN syntax
7. Use table aliases for joins
8. Use valid SQLite syntax only
9. If aggregation is needed:
   - use SUM()
   - COUNT()
   - AVG()
   - GROUP BY correctly
10. Do NOT hallucinate tables or columns
11. Do NOT explain anything
12. Return ONLY SQL query
13. Do NOT use markdown
14. Do NOT wrap SQL in ```sql
15. If question is unrelated to database, return:
    SELECT 'Invalid Question';

USER QUESTION
{question}

OUTPUT
"""


# SQL Error Fix Prompt

def sql_fix_prompt(
    schema_text,
    relationship_text,
    previous_sql,
    error_msg,
    sample_data_text=""
):

    return f"""
You are an expert SQLite SQL debugging assistant.

Your task is to FIX the SQL query using:
- database schema
- relationships
- SQL error message

DATABASE SCHEMA
{schema_text}

TABLE RELATIONSHIP
{relationship_text}


SAMPLE DATA
{sample_data_text}


FAILED SQL QUERY
{previous_sql}

SQL ERROR
{error_msg}

RULES
1. Return ONLY corrected SQL query
2. ONLY SELECT queries allowed
3. Use valid SQLite syntax
4. ONLY use existing tables and columns
5. Always use proper JOINs
6. No explanations
7. No markdown
8. Do NOT wrap in ```sql
9. Keep query optimized and clean

CORRECTED SQL
"""


# Query Explanation Prompt

def explain_result_prompt(question, sql_query, result):

    return f"""
You are a data analyst assistant.

Explain the SQL query result in simple natural language.

USER QUESTION
{question}

SQL QUERY
{sql_query}

QUERY RESULT
{result}

RULES

1. Explain clearly
2. Be concise
3. Mention important insights
4. Use business-friendly language
5. No technical jargon unless needed

EXPLANATION
"""


# SQL Validation Prompt

def validation_prompt(sql_query):

    return f"""
You are a SQL security validator.

Analyze the following SQL query.

SQL QUERY

{sql_query}

TASK
Check whether the query:
- is safe
- is SELECT only
- contains dangerous operations


RETURN FORMAT

SAFE
or
UNSAFE

OUTPUT
"""
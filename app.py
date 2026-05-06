from llm_chain import generate_sql, fix_sql
from database import execute_sql, setup_database

# Setup DB first
setup_database()

print("AskSQL System Ready!")

while True:
    question = input("\nAsk question (or 'exit'): ")

    if question.lower() == "exit":
        print("Exiting...")
        break

    # Step 1: Generate SQL
    sql_query = generate_sql(question)
    print("\nGenerated SQL:", sql_query)

    # Step 2: Execute
    result = execute_sql(sql_query)

    # Step 3: If error → Retry 
    if isinstance(result, str) and "Error" in result:
        print("\n Error detected, retrying with fix...")

        fixed_sql = fix_sql(sql_query, result)
        print("\n Fixed SQL:", fixed_sql)

        result = execute_sql(fixed_sql)

    # Step 4: Output
    print("\n Result:", result)
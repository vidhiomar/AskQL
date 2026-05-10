from llm_chain import (
    generate_sql,
    fix_sql,
    execute_sql
)

from database import (
    get_schema,
    get_relationships,
    schema_to_text,
    relationships_to_text,
    get_sample_data,
    execute_sql
)

# Build DB Context

def build_database_context():

    schema = get_schema()

    relationships = get_relationships()

    schema_text = schema_to_text(schema)

    relationship_text = relationships_to_text(
        relationships
    )

    sample_data_text = get_sample_data()

    return (
        schema_text,
        relationship_text,
        sample_data_text
    )

# Full AskSQL Pipeline

def ask_database(question):

    print("\n" + "=" * 60)
    print("USER QUESTION")
    print("=" * 60)

    print(question)

    # Build DB Context
    (
        schema_text,
        relationship_text,
        sample_data_text
    ) = build_database_context()

    # Generate SQL
    sql_query = generate_sql(
        question=question,
        schema_text=schema_text,
        relationship_text=relationship_text,
        sample_data_text=sample_data_text
    )

    print("\n" + "=" * 60)
    print("GENERATED SQL")
    print("=" * 60)

    print(sql_query)

    # Execute SQL
    result = execute_sql(sql_query)

    # Auto Fix Logic 

    if isinstance(result, str) and "Error" in result:

        print("\n" + "=" * 60)
        print("SQL ERROR DETECTED")
        print("=" * 60)

        print(result)

        print("\n Attempting Auto-Fix...")

        fixed_sql = fix_sql(
            previous_sql=sql_query,
            error_msg=result,
            schema_text=schema_text,
            relationship_text=relationship_text,
            sample_data_text=sample_data_text
        )

        print("\n" + "=" * 60)
        print("FIXED SQL")
        print("=" * 60)

        print(fixed_sql)

        # Retry execution
        result = execute_sql(fixed_sql)

        sql_query = fixed_sql

    # Final Result

    print("\n" + "=" * 60)
    print("QUERY RESULT")
    print("=" * 60)

    print(result)

    # Generate Explanation

    try:

        explanation = explain_result(
            question=question,
            sql_query=sql_query,
            result=result
        )

        print("\n" + "=" * 60)
        print("AI EXPLANATION")
        print("=" * 60)

        print(explanation)

    except Exception as e:

        print("\nExplanation Error:", e)

    print("\n" + "=" * 60)

    return result


# CLI Loop

def run():

    print("\n AskSQL System Started")
    print("Type 'exit' to quit.\n")

    while True:

        question = input("AskSQL > ")

        if question.lower() == "exit":

            print("\nExiting AskSQL...")
            break

        if not question.strip():

            print("Please enter a valid question.")
            continue

        try:

            ask_database(question)

        except Exception as e:

            print("\n Unexpected Error:")
            print(e)


# Main Entry Point

if __name__ == "__main__":

    run()
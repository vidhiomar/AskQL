from llm_chain import (
    generate_sql,
    fix_sql,
    explain_result
)

from db import (
    get_schema,
    get_relationships,
    schema_to_text,
    relationships_to_text,
    get_sample_data,
    execute_sql
)


def build_database_context():

    schema = get_schema()

    relationships = get_relationships()

    schema_text = schema_to_text(
        schema
    )

    relationship_text = relationships_to_text(
        relationships
    )

    sample_data_text = get_sample_data()

    return (
        schema_text,
        relationship_text,
        sample_data_text
    )


def ask_database(question):

    (
        schema_text,
        relationship_text,
        sample_data_text
    ) = build_database_context()

    generated_sql = generate_sql(
        question=question,
        schema_text=schema_text,
        relationship_text=relationship_text,
        sample_data_text=sample_data_text
    )

    result = execute_sql(
        generated_sql
    )

    fixed_sql = None

    # Auto-fix SQL if error occurs
    if isinstance(result, str) and "Error" in result:

        fixed_sql = fix_sql(
            previous_sql=generated_sql,
            error_msg=result,
            schema_text=schema_text,
            relationship_text=relationship_text,
            sample_data_text=sample_data_text
        )

        result = execute_sql(
            fixed_sql
        )

    # Generate explanation
    explanation = explain_result(
        question=question,
        sql_query=fixed_sql if fixed_sql else generated_sql,
        result=result
    )

    return {
        "question": question,
        "generated_sql": generated_sql,
        "fixed_sql": fixed_sql,
        "result": result,
        "explanation": explanation
    }


if __name__ == "__main__":

    while True:

        question = input(
            "\nAskSQL > "
        )

        if question.lower() == "exit":

            break

        response = ask_database(
            question
        )

        print("\nGenerated SQL:")
        print(
            response["generated_sql"]
        )

        if response["fixed_sql"]:

            print("\nFixed SQL:")
            print(
                response["fixed_sql"]
            )

        print("\nResult:")
        print(
            response["result"]
        )

        print("\nExplanation:")
        print(
            response["explanation"]
        )
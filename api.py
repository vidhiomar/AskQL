from fastapi import (FastAPI, UploadFile, File, HTTPException
)
from pydantic import BaseModel
import shutil
import os
import time
from excel_loader import upload_excel_to_db
from app import ask_database

app = FastAPI(
    title="AskSQL API",
    description="AI Powered Natural Language SQL System",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    question: str

@app.get("/")
def home():

    return {
        "success": True,
        "message": "AskSQL API Running"
    }


@app.post("/upload")
async def upload_excel(
    file: UploadFile = File(...)
):

    try:

        allowed_extensions = [
            ".xlsx",
            ".xls",
            ".csv"
        ]

        file_ext = os.path.splitext(
            file.filename
        )[1]

        if file_ext not in allowed_extensions:

            raise HTTPException(
                status_code=400,
                detail="Only Excel files are allowed."
            )

        upload_dir = "uploads"

        os.makedirs(
            upload_dir,
            exist_ok=True
        )

        file_path = os.path.join(
            upload_dir,
            file.filename
        )

        with open(file_path, "wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        result = upload_excel_to_db(
            file_path
        )

        if not result["success"]:

            raise HTTPException(
                status_code=500,
                detail=result["error"]
            )

        return {
            "success": True,
            "message": "Excel uploaded successfully.",
            "table_name": result["table_name"],
            "columns": result["columns"],
            "rows": result["rows"]
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/ask")
def ask_query(request: QueryRequest):

    try:

        start_time = time.time()

        response = ask_database(
            request.question
        )

        end_time = time.time()

        execution_time = round(
            end_time - start_time,
            2
        )

        return {
            "success": True,
            "question": request.question,
            "generated_sql": response.get(
                "generated_sql"
            ),
            "fixed_sql": response.get(
                "fixed_sql"
            ),
            "result": response.get(
                "result"
            ),
            "explanation": response.get(
                "explanation"
            ),
            "execution_time_seconds": execution_time
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
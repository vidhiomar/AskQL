from fastapi import (
    FastAPI, UploadFile , File,HTTPException
)

from pydantic import BaseModel
import shutil
import os
from excel_loader import upload_excel_to_db
from app import ask_database


app = FastAPI(
    title="AskSQL API",
    description="AI Powered Natural Language SQL System",
    version="1.0.0"
)

# Request Model

class QueryRequest(BaseModel):
    question: str

# Root Endpoint

@app.get("/")
def home():

    return {
        "message": "AskSQL API Running"
    }

# Upload Excel Endpoint

@app.post("/upload")
async def upload_excel(
    file: UploadFile = File(...)
):

    try:

        # Validate File Type

        allowed_extensions = [
            ".xlsx",
            ".xls"
        ]

        file_ext = os.path.splitext(
            file.filename
        )[1]

        if file_ext not in allowed_extensions:

            raise HTTPException(
                status_code=400,
                detail="Only Excel files allowed"
            )

        # Save Uploaded File

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

        # Load Excel into DB

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
            "message": "Excel uploaded successfully",
            "data": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# Ask Question Endpoint

@app.post("/ask")
def ask_query(request: QueryRequest):

    try:

        result = ask_database(
            request.question
        )

        return {
            "success": True,
            "question": request.question,
            "result": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
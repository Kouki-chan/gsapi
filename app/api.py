import os
import gradescope
import file_registry
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
import shutil, tempfile

load_dotenv()
app = FastAPI()

email = os.getenv("school_email")
password = os.getenv("password_gradescope")

@app.get("/")
async def root():
    return {"message": "hello world"}

@app.post("/login")
def login():
    attempt = gradescope.login(email, password)
    if "account" in attempt.url:
        return {"status": "success"}
    return {"status": "failed"}

@app.get("/courses")
def courses_route():
    return gradescope.get_courses()

@app.get("/get_assignments")
def get_assignments(course_id: str):
    return gradescope.get_assignments(course_id)

@app.post("/files")
def register_file(name: str, path: str):
    return file_registry.register_file(name, path)

@app.get("/files")
def list_files():
    return file_registry.list_files()

@app.delete("/files/{name}")
def remove_file(name: str):
    return file_registry.remove_file(name)

@app.post("/courses/{course_id}/assignments/{assignment_id}/submit")
def submit_route(course_id: str, assignment_id: str, file_name: str = None, file: UploadFile = File(None)):
    if file_name:
        path = file_registry.get_file_path(file_name)
        if not path:
            return {"error": f"No file registered under '{file_name}'"}
        return gradescope.submit_assignment(course_id, assignment_id, path)
    elif file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        result = gradescope.submit_assignment(course_id, assignment_id, tmp_path)
        os.unlink(tmp_path)
        return result
    return {"error": "Provide either a file_name or upload a file"}
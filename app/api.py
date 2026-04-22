import os
import gradescope
from dotenv import load_dotenv
from fastapi import FastAPI

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
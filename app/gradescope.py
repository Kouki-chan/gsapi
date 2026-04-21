import requests
from bs4 import BeautifulSoup

session = requests.Session()

def login (email: str, password: str):

    login_page = session.get("https://www.gradescope.com/login")
    soup = BeautifulSoup(login_page.text, "html.parser")
    token = soup.find("input", {"name": "authenticity_token"})["value"]

    print(token)

    resp = session.post("https://www.gradescope.com/login", data = {
        "utf8": "✓",
        "authenticity_token": token,
        "session[email]": email,
        "session[password]": password,
        "session[remember_me]": 0,
        "commit": "Log in",
        "session[remember_me_ss0]": 0
        
        
    }, allow_redirects=True)

    return resp

def get_courses():
    page = session.get("https://www.gradescope.com/")
    soup = BeautifulSoup(page.text, "html.parser")

    courses = []
    for course in soup.select("a.courseBox"):
        course_id = course["href"].split("/")[-1] 
        name = course.select_one(".courseBox--shortname")
        full_name = course.select_one(".courseBox--name")
        term = course.select_one(".courseBox--term")

        courses.append({
            "id": course_id,
            "shortname": name.text.strip() if name else "",
            "name": full_name.text.strip() if full_name else "",
            "term": term.text.strip() if term else "",
        })

    return courses

def get_assignments(course_id: str):
    page = session.get(f"https://www.gradescope.com/courses/{course_id}")
    soup = BeautifulSoup(page.text, "html.parser")

    assignments = []
    for row in soup.select("tr[role='row']"):
        button = row.select_one("button.js-submitAssignment")
        status_el = row.select_one(".submissionStatus--text")

        if not button:
            continue

        assignments.append({
            "id": button.get("data-assignment-id", ""),
            "title": button.get("data-assignment-title", ""),
            "status": status_el.text.strip() if status_el else "",
        })
    return assignments

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    email = os.getenv("school_email")
    password = os.getenv("password_gradescope")
    resp = login(email, password)

    print(get_courses())
    print(get_assignments(1233618))

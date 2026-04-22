import os
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
        "session[remember_me_sso]": 0
        
        
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


def upload_assignment(course_id: str, assignment_id: str, file_path:str):
    page = session.get(f"https://www.gradescope.com/courses/{course_id}/assignments/{assignment_id}/submissions/attempt")
    soup = BeautifulSoup(page.txt, "html.parser")
    token = soup.find("meta", {"name": "csrf-token"})

    if not token:
        return {"error": "csrf-token not found"}
    
    csrf = token["content"]

    with open(file_path, "rb") as f:
        resp = session.post(
            f"https://www.gradescope.com/courses/{course_id}/assignments/{assignment_id}/submissions",
            headers={"X-CSRF-Token": csrf},
            files={"submission[files][]": (os.path.basename(file_path), f)},
            data={"authenticity_token": csrf}
        )

    if resp.status_code == 200 or resp.status_code == 201:
        return {"status": "submitted", "assignment_id": assignment_id}
    else:
        return {"status": "failed", "code": resp.status_code}





if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    email = os.getenv("school_email")
    password = os.getenv("password_gradescope")
    resp = login(email, password)

    print(get_courses())
    print(get_assignments(1233618))

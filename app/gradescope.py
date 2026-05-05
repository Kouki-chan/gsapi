import os
import requests
from bs4 import BeautifulSoup

session = requests.Session()

def login(email: str, password: str):
    login_page = session.get("https://www.gradescope.com/login")
    soup = BeautifulSoup(login_page.text, "html.parser")
    token = soup.find("input", {"name": "authenticity_token"})["value"]

    resp = session.post("https://www.gradescope.com/login", data={
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
        link = row.select_one("th.table--primaryLink a")
        status_el = row.select_one(".submissionStatus--text")

        if not link:
            continue

        assignment_id = link["href"].split("/assignments/")[1].split("/")[0]

        assignments.append({
            "id": assignment_id,
            "title": link.text.strip(),
            "status": status_el.text.strip() if status_el else "",
        })

    return assignments

def submit_assignment(course_id: str, assignment_id: str, file_path: str):
    page = session.get(f"https://www.gradescope.com/courses/{course_id}/assignments/{assignment_id}")
    soup = BeautifulSoup(page.text, "html.parser")
    token = soup.find("meta", {"name": "csrf-token"})

    if not token:
        return {"error": "Could not get CSRF token"}

    csrf = token["content"]

    attempt_resp = session.post(
        f"https://www.gradescope.com/courses/{course_id}/assignments/{assignment_id}/submissions/attempt",
        headers={
            "x-csrf-token": csrf,
            "x-requested-with": "XMLHttpRequest",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        },
        data={"submission_event": "opened_submit_assignment_modal"}
    )

    attempt_soup = BeautifulSoup(attempt_resp.text, "html.parser")
    method_input = attempt_soup.find("input", {"name": "submission[method_id]"})
    if not method_input:
        return {"error": "Could not find submission method_id"}
    method_id = method_input["value"]

    with open(file_path, "rb") as f:
        resp = session.post(
            f"https://www.gradescope.com/courses/{course_id}/assignments/{assignment_id}/submissions",
            headers={
                "accept": "application/json",
                "x-csrf-token": csrf,
                "x-requested-with": "XMLHttpRequest",
            },
            data={"submission[method_id]": method_id},
            files={
                "submission[files][]": (os.path.basename(file_path), f, "application/octet-stream")
            }
        )

    print(resp.status_code)
    print(resp.text)

    if resp.status_code == 200:
        return {"status": "submitted", "response": resp.json()}
    else:
        return {"status": "failed", "code": resp.status_code, "response": resp.text}


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    email = os.getenv("school_email")
    password = os.getenv("password_gradescope")
    resp = login(email, password)

    #print (resp)

    courses = get_courses()
    #print (courses)

    assignments = get_assignments(1131329)
    print (assignments)

    # result = submit_assignment("1131329", "8089078", r"C:\Users\kevin\workspace\j--\src\jminusminus\Parser.java")
    # print(result)
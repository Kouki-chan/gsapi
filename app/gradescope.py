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
    import json as _json

    page = session.get(f"https://www.gradescope.com/courses/{course_id}/assignments/{assignment_id}")
    soup = BeautifulSoup(page.text, "html.parser")

    token = soup.find("meta", {"name": "csrf-token"})
    if not token:
        return {"error": "Could not get CSRF token"}
    csrf = token["content"]

    # Try to find method_id from a hidden input on the assignment page
    method_id = None
    method_input = soup.find("input", {"name": "submission[method_id]"})
    if method_input:
        method_id = method_input["value"]

    # Fall back to React props embedded in the page
    if not method_id:
        for tag in soup.find_all(attrs={"data-react-props": True}):
            try:
                props = _json.loads(tag["data-react-props"])
                methods = props.get("submissionMethods") or props.get("submission_methods", [])
                if methods:
                    method_id = str(methods[0]["id"])
                    break
            except Exception:
                pass

    session.post(
        f"https://www.gradescope.com/courses/{course_id}/assignments/{assignment_id}/submissions/attempt",
        headers={
            "x-csrf-token": csrf,
            "x-requested-with": "XMLHttpRequest",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        },
        data={"submission_event": "opened_submit_assignment_modal"}
    )

    form_data = {}
    if method_id:
        form_data["submission[method_id]"] = method_id

    with open(file_path, "rb") as f:
        resp = session.post(
            f"https://www.gradescope.com/courses/{course_id}/assignments/{assignment_id}/submissions",
            headers={
                "accept": "application/json",
                "x-csrf-token": csrf,
                "x-requested-with": "XMLHttpRequest",
            },
            data=form_data,
            files={
                "submission[files][]": (os.path.basename(file_path), f, "application/octet-stream")
            }
        )

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
    # print (assignments)

    result = submit_assignment("1131329", "8089078", r"C:\Users\kevin\workspace\iota\register_allocation\notes.txt")
    print(result)
    
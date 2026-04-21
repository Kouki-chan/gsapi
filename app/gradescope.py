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

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    email = os.getenv("school_email")
    password = os.getenv("password_gradescope")
    print(email)
    print(password)
    resp = login(email, password)
    print(resp.url)
    print(resp.status_code)
    # print(attempt.text[:2000])

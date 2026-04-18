import os
from dotenv import load_dotenv


load_dotenv()

# grabbing login info
email = os.getenv("school_email")
password = os.getenv("password_gradescope")

print (email, password)




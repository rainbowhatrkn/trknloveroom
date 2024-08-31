from flask import Flask
from flask_bcrypt import Bcrypt
from replit import db

app = Flask(__name__)
bcrypt = Bcrypt(app)

def promote_user_to_admin(email):
    users = db.get("users", [])
    user_found = False

    for user in users:
        if user["email"] == email:
            user["is_admin"] = True
            user_found = True
            break

    if not user_found:
        print(f"User with email {email} not found.")
        return

    db["users"] = users
    print(f"User with email {email} has been promoted to admin.")

if __name__ == "__main__":
    user_email = "jeremydiliotti@gmail.com"
    promote_user_to_admin(user_email)
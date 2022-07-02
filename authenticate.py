from sql_db import insert_data, get_data
from hashlib import sha256

def auth(password, email=None):
    password = sha256(password.encode()).hexdigest()
    result = None
    if email:
        result = get_data(email=email)
    print(result)
    print(password)
    if result and len(result) == 9:
        if result[2] == password:
            return True
    return False

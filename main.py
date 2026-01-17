from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import csv
import os

app = FastAPI()

class LoginRequest(BaseModel):
    username: str
    password: str

def validate_credentials(username: str, password: str) -> bool:
    """
    Validate username and password against the CSV file 'unpw'.
    Returns True if credentials are valid, False otherwise.
    """
    csv_file = os.path.join(os.path.dirname(__file__), "unpw")

    try:
        with open(csv_file, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    stored_username, stored_password = line.split(',', 1)
                    if stored_username == username and stored_password == password:
                        return True
        return False
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Credentials file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading credentials: {str(e)}")

@app.post("/login")
async def login(request: LoginRequest):
    """
    Login endpoint that validates username and password against CSV file.
    Returns success message if credentials are valid.
    """
    if validate_credentials(request.username, request.password):
        return {"message": "login success"}
    else:
        raise HTTPException(status_code=401, detail="error message")

@app.get("/")
async def root():
    return {"message": "Welcome to the login API. Use POST /login to authenticate."}

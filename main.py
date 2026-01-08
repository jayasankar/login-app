from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login(request: LoginRequest):
    """
    Simple login endpoint that accepts username and password.
    Only accepts username='test' and password='test'.
    """
    if request.username == "test" and request.password == "test":
        return {"message": "login success"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/")
async def root():
    return {"message": "Welcome to the login API. Use POST /login to authenticate."}

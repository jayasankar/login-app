from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
import time
from csv_loader import load_credentials_from_csv, get_credentials_map
from logger import get_logger, log_json

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown.
    Loads credentials from CSV file into hashmap at application startup.
    """
    load_credentials_from_csv()
    yield


app = FastAPI(lifespan=lifespan)


class LoginRequest(BaseModel):
    username: str
    password: str


def validate_credentials(username: str, password: str) -> bool:
    """
    Validate username and password against the credentials hashmap.
    Returns True if credentials are valid, False otherwise.
    """
    validation_start_time = time.time()

    try:
        credentials_map = get_credentials_map()

        # Check if credentials hashmap is loaded
        if not credentials_map:
            log_json(logger, 'error', {
                "event": "validation_error",
                "username": username,
                "error": "credentials_not_loaded"
            })
            raise HTTPException(status_code=500, detail="Credentials not loaded")

        # O(1) lookup in hashmap
        stored_password = credentials_map.get(username)
        validation_duration = (time.time() - validation_start_time) * 1000

        if stored_password and stored_password == password:
            log_json(logger, 'info', {
                "event": "hashmap_validation",
                "username": username,
                "result": "found",
                "validation_duration_ms": round(validation_duration, 2)
            })
            return True
        else:
            log_json(logger, 'info', {
                "event": "hashmap_validation",
                "username": username,
                "result": "not_found",
                "validation_duration_ms": round(validation_duration, 2)
            })
            return False
    except HTTPException:
        raise
    except Exception as e:
        log_json(logger, 'error', {
            "event": "validation_error",
            "username": username,
            "error": str(e)
        })
        raise HTTPException(
            status_code=500, detail=f"Error validating credentials: {str(e)}"
        )


@app.post("/login")
async def login(request: LoginRequest):
    """
    Login endpoint that validates username and password against CSV file.
    Returns success message if credentials are valid.
    """
    request_start_time = time.time()

    log_json(logger, 'info', {
        "event": "login_request_received",
        "username": request.username,
        "endpoint": "/login"
    })

    try:
        if validate_credentials(request.username, request.password):
            request_duration = (time.time() - request_start_time) * 1000
            log_json(logger, 'info', {
                "event": "login_success",
                "username": request.username,
                "status_code": 200,
                "total_duration_ms": round(request_duration, 2)
            })
            return {"message": "login success"}
        else:
            request_duration = (time.time() - request_start_time) * 1000
            log_json(logger, 'warning', {
                "event": "login_failed",
                "username": request.username,
                "reason": "invalid_credentials",
                "status_code": 401,
                "total_duration_ms": round(request_duration, 2)
            })
            raise HTTPException(status_code=401, detail="error message")
    except HTTPException as e:
        if e.status_code != 401:
            request_duration = (time.time() - request_start_time) * 1000
            log_json(logger, 'error', {
                "event": "login_error",
                "username": request.username,
                "status_code": e.status_code,
                "error": e.detail,
                "total_duration_ms": round(request_duration, 2)
            })
        raise


@app.get("/")
async def root():
    return {"message": "Welcome to the login API. Use POST /login to authenticate."}

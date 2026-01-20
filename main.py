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


class PasswordResetRequest(BaseModel):
    username: str


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


@app.post("/password-reset")
async def password_reset(request: PasswordResetRequest):
    """
    Password reset endpoint that checks if username exists in the credentials file.
    Returns success message if user exists, fail message otherwise.
    Note: Actual password reset logic is not implemented yet.
    """
    request_start_time = time.time()

    log_json(logger, 'info', {
        "event": "password_reset_request_received",
        "username": request.username,
        "endpoint": "/password-reset"
    })

    try:
        credentials_map = get_credentials_map()

        # Check if credentials hashmap is loaded
        if not credentials_map:
            log_json(logger, 'error', {
                "event": "password_reset_error",
                "username": request.username,
                "error": "credentials_not_loaded"
            })
            raise HTTPException(status_code=500, detail="Credentials not loaded")

        # Check if user exists in the credentials
        if request.username in credentials_map:
            request_duration = (time.time() - request_start_time) * 1000
            log_json(logger, 'info', {
                "event": "password_reset_success",
                "username": request.username,
                "status_code": 200,
                "total_duration_ms": round(request_duration, 2)
            })
            # TODO: Implement actual password reset logic here
            return {"message": "success", "detail": "Password reset initiated. Check your email for instructions."}
        else:
            request_duration = (time.time() - request_start_time) * 1000
            log_json(logger, 'warning', {
                "event": "password_reset_failed",
                "username": request.username,
                "reason": "user_not_found",
                "status_code": 404,
                "total_duration_ms": round(request_duration, 2)
            })
            return {"message": "fail", "detail": "User not found"}
    except HTTPException:
        raise
    except Exception as e:
        request_duration = (time.time() - request_start_time) * 1000
        log_json(logger, 'error', {
            "event": "password_reset_error",
            "username": request.username,
            "error": str(e),
            "total_duration_ms": round(request_duration, 2)
        })
        raise HTTPException(
            status_code=500, detail=f"Error processing password reset: {str(e)}"
        )


@app.get("/")
async def root():
    return {"message": "Welcome to the login API. Use POST /login to authenticate."}

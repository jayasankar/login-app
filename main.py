from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import logging
import time
import json

# Configure logging with structured format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

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
    csv_start_time = time.time()

    try:
        with open(csv_file, "r") as file:
            line_count = 0
            for line in file:
                line_count += 1
                line = line.strip()
                if line:
                    stored_username, stored_password = line.split(",", 1)
                    if stored_username == username and stored_password == password:
                        csv_duration = (time.time() - csv_start_time) * 1000
                        logger.info(json.dumps({
                            "event": "csv_validation",
                            "username": username,
                            "result": "found",
                            "lines_scanned": line_count,
                            "csv_read_duration_ms": round(csv_duration, 2)
                        }))
                        return True

        csv_duration = (time.time() - csv_start_time) * 1000
        logger.info(json.dumps({
            "event": "csv_validation",
            "username": username,
            "result": "not_found",
            "lines_scanned": line_count,
            "csv_read_duration_ms": round(csv_duration, 2)
        }))
        return False
    except FileNotFoundError:
        logger.error(json.dumps({
            "event": "csv_validation_error",
            "username": username,
            "error": "credentials_file_not_found"
        }))
        raise HTTPException(status_code=500, detail="Credentials file not found")
    except Exception as e:
        logger.error(json.dumps({
            "event": "csv_validation_error",
            "username": username,
            "error": str(e)
        }))
        raise HTTPException(
            status_code=500, detail=f"Error reading credentials: {str(e)}"
        )


@app.post("/login")
async def login(request: LoginRequest):
    """
    Login endpoint that validates username and password against CSV file.
    Returns success message if credentials are valid.
    """
    request_start_time = time.time()

    logger.info(json.dumps({
        "event": "login_request_received",
        "username": request.username,
        "endpoint": "/login"
    }))

    try:
        if validate_credentials(request.username, request.password):
            request_duration = (time.time() - request_start_time) * 1000
            logger.info(json.dumps({
                "event": "login_success",
                "username": request.username,
                "status_code": 200,
                "total_duration_ms": round(request_duration, 2)
            }))
            return {"message": "login success"}
        else:
            request_duration = (time.time() - request_start_time) * 1000
            logger.warning(json.dumps({
                "event": "login_failed",
                "username": request.username,
                "reason": "invalid_credentials",
                "status_code": 401,
                "total_duration_ms": round(request_duration, 2)
            }))
            raise HTTPException(status_code=401, detail="error message")
    except HTTPException as e:
        if e.status_code != 401:
            request_duration = (time.time() - request_start_time) * 1000
            logger.error(json.dumps({
                "event": "login_error",
                "username": request.username,
                "status_code": e.status_code,
                "error": e.detail,
                "total_duration_ms": round(request_duration, 2)
            }))
        raise


@app.get("/")
async def root():
    return {"message": "Welcome to the login API. Use POST /login to authenticate."}

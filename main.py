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

# Global hashmap to store credentials loaded at startup
credentials_map: dict[str, str] = {}


class LoginRequest(BaseModel):
    username: str
    password: str


@app.on_event("startup")
async def load_credentials():
    """
    Load credentials from CSV file into hashmap at application startup.
    """
    csv_file = os.path.join(os.path.dirname(__file__), "unpw")
    load_start_time = time.time()

    try:
        with open(csv_file, "r") as file:
            line_count = 0
            for line in file:
                line = line.strip()
                if line:
                    stored_username, stored_password = line.split(",", 1)
                    credentials_map[stored_username] = stored_password
                    line_count += 1

        load_duration = (time.time() - load_start_time) * 1000
        logger.info(json.dumps({
            "event": "credentials_loaded",
            "credentials_count": line_count,
            "load_duration_ms": round(load_duration, 2)
        }))
    except FileNotFoundError:
        logger.error(json.dumps({
            "event": "credentials_load_error",
            "error": "credentials_file_not_found"
        }))
    except Exception as e:
        logger.error(json.dumps({
            "event": "credentials_load_error",
            "error": str(e)
        }))


def validate_credentials(username: str, password: str) -> bool:
    """
    Validate username and password against the credentials hashmap.
    Returns True if credentials are valid, False otherwise.
    """
    validation_start_time = time.time()

    try:
        # Check if credentials hashmap is loaded
        if not credentials_map:
            logger.error(json.dumps({
                "event": "validation_error",
                "username": username,
                "error": "credentials_not_loaded"
            }))
            raise HTTPException(status_code=500, detail="Credentials not loaded")

        # O(1) lookup in hashmap
        stored_password = credentials_map.get(username)
        validation_duration = (time.time() - validation_start_time) * 1000

        if stored_password and stored_password == password:
            logger.info(json.dumps({
                "event": "hashmap_validation",
                "username": username,
                "result": "found",
                "validation_duration_ms": round(validation_duration, 2)
            }))
            return True
        else:
            logger.info(json.dumps({
                "event": "hashmap_validation",
                "username": username,
                "result": "not_found",
                "validation_duration_ms": round(validation_duration, 2)
            }))
            return False
    except HTTPException:
        raise
    except Exception as e:
        logger.error(json.dumps({
            "event": "validation_error",
            "username": username,
            "error": str(e)
        }))
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

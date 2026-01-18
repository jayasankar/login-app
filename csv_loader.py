import os
import time
from logger import get_logger, log_json

logger = get_logger(__name__)

# Global hashmap to store credentials loaded at startup
credentials_map: dict[str, str] = {}


def load_credentials_from_csv(csv_file_path: str = None) -> dict[str, str]:
    """
    Load credentials from CSV file into hashmap.

    Args:
        csv_file_path: Path to the CSV file. If None, defaults to 'unpw' in the same directory.

    Returns:
        Dictionary mapping usernames to passwords
    """
    if csv_file_path is None:
        csv_file_path = os.path.join(os.path.dirname(__file__), "unpw")

    load_start_time = time.time()

    try:
        with open(csv_file_path, "r") as file:
            line_count = 0
            for line in file:
                line = line.strip()
                if line:
                    stored_username, stored_password = line.split(",", 1)
                    credentials_map[stored_username] = stored_password
                    line_count += 1

        load_duration = (time.time() - load_start_time) * 1000
        log_json(logger, 'info', {
            "event": "credentials_loaded",
            "credentials_count": line_count,
            "load_duration_ms": round(load_duration, 2)
        })
    except FileNotFoundError:
        log_json(logger, 'error', {
            "event": "credentials_load_error",
            "error": "credentials_file_not_found"
        })
    except Exception as e:
        log_json(logger, 'error', {
            "event": "credentials_load_error",
            "error": str(e)
        })

    return credentials_map


def get_credentials_map() -> dict[str, str]:
    """
    Get the current credentials map.

    Returns:
        Dictionary mapping usernames to passwords
    """
    return credentials_map

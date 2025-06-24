import requests
import os
import sys
import json
import tempfile
import logging
import time

# Configuration block: these variables can be set via environment for flexibility in automation
ENDPOINT = os.environ.get("REMOTE_ENV_ENDPOINT", "http://mockserver:8000/env")  # HTTP endpoint for fetching env variables
VARS = os.environ.get("REMOTE_ENV_VARS", "DB_HOST,REDIS_URL,SECRET_KEY")        # Comma-separated list of variables to sync
AUTH_USER = os.environ.get("REMOTE_ENV_USER", "user")                           # Username for basic auth
AUTH_PASS = os.environ.get("REMOTE_ENV_PASS", "pass")                           # Password for basic auth
TARGET_FILE = os.environ.get("REMOTE_ENV_TARGET_FILE", "/etc/profile.d/remote_env.sh")  # Path to write synced variables

# Configure logging to output timestamp, log level, and message
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def fetch_env_vars():
    """
    Fetch environment variables from central endpoint via HTTP GET.
    Exits if the request fails or returns invalid data.
    """
    try:
        response = requests.get(
            ENDPOINT,
            params={"vars": VARS},
            auth=(AUTH_USER, AUTH_PASS),
            timeout=5,
            verify=False  # Disable SSL verification for test/mock endpoints; enable for production
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("Malformed response: not a dict")
        return data
    except Exception as e:
        logging.error(f"Failed to fetch env vars: {e}")
        sys.exit(1)

def atomic_write_env_file(env_vars, target_file):
    """
    Atomically write environment variables to a target file.
    This function writes to a temp file, then moves it over the target to avoid race conditions.
    File permissions are set to 600 for security.
    """
    # Write variables to a temporary file first
    dir_name = os.path.dirname(target_file)
    fd, temp_path = tempfile.mkstemp(dir=dir_name)
    with os.fdopen(fd, 'w') as tmp:
        for key, value in env_vars.items():
            tmp.write(f'export {key}="{value}"\n')
    # Set file permissions to 600 (rw-------)
    os.chmod(temp_path, 0o600)
    # Atomically move the temp file to the target location
    os.replace(temp_path, target_file)
    logging.info(f"Env vars written to {target_file}")

def main():
    """
    Main workflow: fetch variables and write them atomically to the target file.
    """
    env_vars = fetch_env_vars()
    atomic_write_env_file(env_vars, TARGET_FILE)

if __name__ == "__main__":
    main()

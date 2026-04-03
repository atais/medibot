"""
Pytest fixtures for E2E tests.

Starts a real uvicorn process with test env vars, waits until it's healthy,
then tears it down after the session.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests

BASE_URL = "http://127.0.0.1:8765"

# Absolute paths so the subprocess can find files regardless of cwd
REPO_ROOT = Path(__file__).parent.parent
TEST_SA = REPO_ROOT / "tests" / "firebase-service-account.test.json"
TEST_DB = REPO_ROOT / "tests" / "test.sqlite"

TEST_ENV = {
    **os.environ,
    "APP_DB": f"sqlite:///{TEST_DB}",
    "SESSION_KEY": "test-session-secret-key-for-ci",
    "APP_ADMINS": "000000",
    "FCM_SERVICE_ACCOUNT_PATH": str(TEST_SA),
    # Dummy Firebase config – the login page renders these into JS,
    # but no real Firebase calls happen during this test.
    "FIREBASE_API_KEY": "test-api-key",
    "FIREBASE_AUTH_DOMAIN": "medibot-test.firebaseapp.com",
    "FIREBASE_PROJECT_ID": "medibot-test",
    "FIREBASE_STORAGE_BUCKET": "medibot-test.appspot.com",
    "FIREBASE_MESSAGING_SENDER_ID": "000000000000",
    "FIREBASE_APP_ID": "1:000000000000:web:0000000000000000",
    "FIREBASE_VAPID_KEY": "test-vapid-key",
}


@pytest.fixture(scope="session")
def app_server():
    """Start uvicorn in a subprocess and yield the base URL."""
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn",
            "app:app",
            "--host", "127.0.0.1",
            "--port", "8765",
        ],
        cwd=str(REPO_ROOT),
        env=TEST_ENV,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    # Wait up to 15 s for the server to accept requests
    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            r = requests.get(f"{BASE_URL}/login", timeout=2)
            if r.status_code < 500:
                break
        except requests.exceptions.ConnectionError:
            time.sleep(0.3)
    else:
        proc.kill()
        out, _ = proc.communicate()
        raise RuntimeError(
            f"App server did not start in time.\nOutput:\n{out.decode()}"
        )

    yield BASE_URL

    proc.kill()
    proc.wait()


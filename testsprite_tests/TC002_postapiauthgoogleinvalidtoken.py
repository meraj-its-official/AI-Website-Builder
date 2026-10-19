import requests
import sys
import json

BASE_URL = "http://localhost:8000"
AUTH_GOOGLE_PATH = "/api/auth/google"
PROTECTED_WEBSITE_PATH = "/api/website"
TIMEOUT = 30

def test_post_api_auth_google_invalid_token_TC002():
    headers = {"Content-Type": "application/json"}
    url = BASE_URL + AUTH_GOOGLE_PATH

    try:
        # Case 1: Missing identity token (empty body)
        resp_missing = requests.post(url, headers=headers, json={}, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise AssertionError(f"Request failed for missing token case: {e}")

    # Assert authentication error status
    assert resp_missing.status_code == 401, (
        f"Expected 401 for missing identity token, got {resp_missing.status_code}. Response body: {resp_missing.text}"
    )
    # Assert no session cookie was issued
    assert not resp_missing.headers.get("Set-Cookie"), (
        f"Expected no Set-Cookie header for missing token, but got: {resp_missing.headers.get('Set-Cookie')}"
    )
    assert len(resp_missing.cookies) == 0, "Expected no cookies to be set for missing token response"

    try:
        # Case 2: Invalid identity token
        invalid_payload = {"idToken": "invalid-or-malformed-token"}
        resp_invalid = requests.post(url, headers=headers, json=invalid_payload, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise AssertionError(f"Request failed for invalid token case: {e}")

    # Assert authentication error status
    assert resp_invalid.status_code == 401, (
        f"Expected 401 for invalid identity token, got {resp_invalid.status_code}. Response body: {resp_invalid.text}"
    )
    # Assert no session cookie was issued
    assert not resp_invalid.headers.get("Set-Cookie"), (
        f"Expected no Set-Cookie header for invalid token, but got: {resp_invalid.headers.get('Set-Cookie')}"
    )
    assert len(resp_invalid.cookies) == 0, "Expected no cookies to be set for invalid token response"

    # Verify protected route remains inaccessible without a valid session
    try:
        resp_protected = requests.get(BASE_URL + PROTECTED_WEBSITE_PATH, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise AssertionError(f"Request failed when accessing protected route without session: {e}")

    assert resp_protected.status_code == 401, (
        f"Expected 401 when accessing protected route without session, got {resp_protected.status_code}. Response body: {resp_protected.text}"
    )

    print("TC002 passed: POST /api/auth/google rejects missing/invalid tokens and does not create a session.")

if __name__ == "__main__":
    try:
        test_post_api_auth_google_invalid_token_TC002()
    except AssertionError as e:
        print("TC002 failed:", e)
        sys.exit(1)
    except Exception as e:
        print("TC002 encountered an unexpected error:", e)
        sys.exit(2)
    sys.exit(0)
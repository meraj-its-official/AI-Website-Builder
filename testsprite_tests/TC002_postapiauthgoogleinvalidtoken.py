import requests
import sys

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_post_api_auth_google_invalid_token():
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    def has_set_cookie(response):
        return any(k.lower() == "set-cookie" for k in response.headers.keys()) or bool(response.cookies)

    # 1) POST with missing identity token (provide required email but empty idToken)
    payload_missing = {"email": "test@example.com", "idToken": ""}
    try:
        resp_missing = requests.post(f"{BASE_URL}/api/auth/google", headers=headers, json=payload_missing, timeout=TIMEOUT)
    except requests.exceptions.RequestException as e:
        raise AssertionError(f"Request to POST /api/auth/google (missing token) failed: {e}")

    assert resp_missing.status_code == 401, \
        f"Expected 401 for missing identity token, got {resp_missing.status_code}. Body: {resp_missing.text}"
    assert not has_set_cookie(resp_missing), "Server set a session cookie for missing/invalid token (should not)"

    # 2) POST with an explicitly invalid identity token (include required email)
    invalid_payload = {"email": "test@example.com", "idToken": "this-is-an-invalid-token-12345"}
    try:
        resp_invalid = requests.post(f"{BASE_URL}/api/auth/google", headers=headers, json=invalid_payload, timeout=TIMEOUT)
    except requests.exceptions.RequestException as e:
        raise AssertionError(f"Request to POST /api/auth/google (invalid token) failed: {e}")

    assert resp_invalid.status_code == 401, \
        f"Expected 401 for invalid identity token, got {resp_invalid.status_code}. Body: {resp_invalid.text}"
    assert not has_set_cookie(resp_invalid), "Server set a session cookie for missing/invalid token (should not)"

    # 3) Verify protected route remains inaccessible without a valid session
    try:
        resp_protected = requests.get(f"{BASE_URL}/api/website", headers={"Accept": "application/json"}, timeout=TIMEOUT)
    except requests.exceptions.RequestException as e:
        raise AssertionError(f"Request to GET /api/website failed: {e}")

    assert resp_protected.status_code == 401, \
        f"Expected 401 when accessing protected route without session, got {resp_protected.status_code}. Body: {resp_protected.text}"

    print("TC002 passed: POST /api/auth/google returns 401 for missing/invalid token and no session is created.")

if __name__ == "__main__":
    try:
        test_post_api_auth_google_invalid_token()
    except AssertionError as e:
        print(f"TEST FAILURE: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
        sys.exit(2)
    print("All checks completed successfully.")
    sys.exit(0)

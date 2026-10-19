import os
import requests
import sys

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_post_api_auth_google_valid_token():
    token = os.getenv("TEST_GOOGLE_ID_TOKEN")
    if not token:
        raise RuntimeError("Environment variable TEST_GOOGLE_ID_TOKEN must be set to a valid Google identity token for this test.")

    session = requests.Session()
    url = f"{BASE_URL}/api/auth/google"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    # Send common token fields to increase compatibility with different backends
    payload = {
        "idToken": token,
        "credential": token
    }

    try:
        resp = session.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise AssertionError(f"Request to {url} failed: {e}")

    assert resp.status_code == 200, f"Expected 200 from {url}, got {resp.status_code}. Body: {resp.text}"

    try:
        data = resp.json()
    except ValueError:
        raise AssertionError(f"Response from {url} is not valid JSON. Raw body: {resp.text}")

    expected_keys = {"user", "session", "token", "id", "email"}
    if not any(k in data for k in expected_keys):
        raise AssertionError(f"Response JSON does not contain expected user/session keys. JSON: {data}")

    # Verify a session cookie was set
    set_cookie_header = resp.headers.get("set-cookie")
    has_cookie = bool(resp.cookies) or bool(set_cookie_header)
    assert has_cookie, f"No session cookie set in response. cookies: {resp.cookies}, set-cookie: {set_cookie_header}"

    # Use the session (which holds cookies) to access a protected route
    protected_url = f"{BASE_URL}/api/user/me"
    try:
        protected_resp = session.get(protected_url, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise AssertionError(f"Request to protected route {protected_url} failed: {e}")

    assert protected_resp.status_code == 200, f"Expected 200 from protected route {protected_url}, got {protected_resp.status_code}. Body: {protected_resp.text}"

    try:
        protected_data = protected_resp.json()
    except ValueError:
        raise AssertionError(f"Protected route {protected_url} did not return JSON. Raw body: {protected_resp.text}")

    if not any(k in protected_data for k in ("email", "id", "user")):
        raise AssertionError(f"Protected route returned JSON but missing expected user fields: {protected_data}")

    print("TC001 passed: POST /api/auth/google returned 200, set session cookie, and protected route is accessible.")

if __name__ == "__main__":
    try:
        test_post_api_auth_google_valid_token()
    except AssertionError as e:
        print(f"TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(2)
    else:
        sys.exit(0)
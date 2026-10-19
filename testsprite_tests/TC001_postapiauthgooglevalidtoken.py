import os
import sys
import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_postapiauthgooglevalidtoken():
    """
    TC001 - postapiauthgooglevalidtoken
    - Validate landing page loads
    - POST /api/auth/google with a valid Google identity token (from env TEST_GOOGLE_ID_TOKEN)
    - Expect 200 and Set-Cookie header (session cookie)
    - Use returned cookie to access a protected route (/api/website) and expect 200
    """
    token = os.environ.get("TEST_GOOGLE_ID_TOKEN")
    assert token, "TEST_GOOGLE_ID_TOKEN environment variable is required for this test."

    # 1) Validate landing page loads
    try:
        r_home = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
    except requests.RequestException as e:
        raise AssertionError(f"Failed to load landing page {BASE_URL}/ : {e}") from e
    assert r_home.status_code == 200, f"Landing page returned unexpected status: {r_home.status_code}"
    # Check for basic expected content markers to ensure page rendered
    home_text = r_home.text or ""
    assert ("ConTex" in home_text) or ("AI Website" in home_text) or ("<div" in home_text), "Landing page content does not contain expected markers."

    session = requests.Session()

    # 2) POST /api/auth/google with valid identity token
    payload = {"idToken": token}
    headers = {"Content-Type": "application/json"}
    try:
        r_auth = session.post(f"{BASE_URL}/api/auth/google", json=payload, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise AssertionError(f"Auth request failed: {e}") from e

    # Validate successful authentication
    if r_auth.status_code != 200:
        # include server response to help debugging
        raise AssertionError(f"Expected 200 from /api/auth/google, got {r_auth.status_code}. Response body: {r_auth.text}")

    # Check that server attempted to set a session cookie
    set_cookie_header = None
    # headers lookups are case-insensitive via dict interface, but normalize for safety
    for k, v in r_auth.headers.items():
        if k.lower() == "set-cookie":
            set_cookie_header = v
            break
    assert set_cookie_header, "Authentication response did not include Set-Cookie header for session."

    # Ensure session object captured cookies
    # session.cookies may be empty if cookie domain/path mismatches, but at minimum response had Set-Cookie
    if not session.cookies:
        # still allow, but warn via assertion message if this leads to protected route failure later
        pass

    # 3) Access a protected route using the session cookie
    try:
        r_protected = session.get(f"{BASE_URL}/api/website", timeout=TIMEOUT)
    except requests.RequestException as e:
        raise AssertionError(f"Protected route request failed: {e}") from e

    # Expect 200 OK for protected resource when authenticated
    if r_protected.status_code != 200:
        raise AssertionError(f"Authenticated request to /api/website expected 200 but got {r_protected.status_code}. Response body: {r_protected.text}")

    # 4) Validate auth response JSON contains user/session data (best-effort)
    try:
        auth_json = r_auth.json()
    except ValueError:
        auth_json = None

    if auth_json is not None:
        # Expect some user/session identifying fields
        has_user_fields = any(k in auth_json for k in ("user", "session", "token", "id", "email"))
        assert has_user_fields, f"Auth response JSON does not contain expected user/session fields: {auth_json}"

    print("TC001 passed: POST /api/auth/google with valid token succeeded and session cookie established.")


if __name__ == "__main__":
    try:
        test_postapiauthgooglevalidtoken()
    except AssertionError as e:
        print(f"TC001 FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"TC001 ERROR: Unexpected exception: {e}")
        sys.exit(2)
    else:
        sys.exit(0)
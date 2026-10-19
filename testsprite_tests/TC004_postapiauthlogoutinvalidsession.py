import requests
from requests.exceptions import RequestException, Timeout

BASE_URL = "http://localhost:8000"
TIMEOUT = 30  # seconds

def test_post_api_auth_logout_invalid_session():
    """
    TC004 - postapiauthlogoutinvalidsession
    Test POST /api/auth/logout without a valid session cookie to verify
    it returns an authentication error or appropriate failure response.
    Also validate the landing page loads and some key UI elements are present.
    """
    # Validate landing page loads and basic UI
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
    except (RequestException, Timeout) as e:
        raise AssertionError(f"Failed to GET landing page at {BASE_URL}/: {e}")

    assert resp.status_code == 200, f"Landing page did not return 200 OK, got {resp.status_code}"
    body = resp.text or ""
    # Check for expected content -- project name or sign-in element
    assert ("ConTex" in body) or ("Sign" in body) or ("Sign In" in body) or ("Sign in" in body), \
        "Landing page HTML does not contain expected UI text (ConTex / Sign In)."

    # Attempt to logout without sending any session cookie
    logout_url = f"{BASE_URL}/api/auth/logout"
    headers = {"Content-Type": "application/json"}

    try:
        logout_resp = requests.post(logout_url, headers=headers, timeout=TIMEOUT)
    except (RequestException, Timeout) as e:
        raise AssertionError(f"Request to POST {logout_url} failed: {e}")

    # Expect an authentication error or appropriate failure when no session is provided.
    # Accept common auth-related status codes: 401 Unauthorized or 403 Forbidden.
    acceptable_statuses = {401, 403}
    if logout_resp.status_code in acceptable_statuses:
        # If JSON, try to assert there's an error message
        content_type = logout_resp.headers.get("Content-Type", "")
        if "application/json" in content_type:
            try:
                payload = logout_resp.json()
                # expect some indication of authentication failure
                assert any(k in payload for k in ("error", "message", "msg", "status")), \
                    "Auth error response JSON did not contain expected keys (error/message/msg/status)."
            except ValueError:
                raise AssertionError("Logout response declared JSON but body could not be parsed.")
        # Test passes for expected auth failure status
        return
    else:
        # If server returns 200, 204, or other codes, treat as failure for this test case
        raise AssertionError(
            f"Expected authentication failure (401/403) when calling POST {logout_url} without session cookie, "
            f"but received HTTP {logout_resp.status_code}. Response body: {logout_resp.text}"
        )

if __name__ == "__main__":
    test_post_api_auth_logout_invalid_session()
    print("TC004 passed.")
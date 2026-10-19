import requests
import sys

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_postapiauthlogoutinvalidsession():
    """
    TC004: POST /api/auth/logout without a valid session cookie should either succeed (idempotent logout)
    or return an authentication/failure response. Accept 200, 400, 401, 403, 404 as valid outcomes.
    """
    url = f"{BASE_URL}/api/auth/logout"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        resp = requests.post(url, headers=headers, timeout=TIMEOUT)
    except requests.exceptions.RequestException as e:
        raise AssertionError(f"HTTP request failed: {e}")

    # Accept common success or authentication/failure status codes
    allowed_codes = {200, 400, 401, 403, 404}
    assert resp.status_code in allowed_codes, f"Unexpected status code: {resp.status_code}. Body: {resp.text}"

    # If response is JSON, ensure it indicates either success or an error/message about authentication.
    try:
        body = resp.json()
    except ValueError:
        # Non-JSON body is acceptable as long as status code is in allowed codes
        return

    if resp.status_code == 200:
        # Expect indication of successful logout: message or success flag
        if not any(k in body for k in ("message", "success", "status", "code")):
            raise AssertionError(f"200 response JSON did not contain expected success fields: {body}")
        if "success" in body:
            assert bool(body.get("success")), f"Expected success=true for 200 response, got: {body.get('success')}"
        # If message exists, ensure it's non-empty
        if "message" in body:
            assert isinstance(body.get("message"), str) and body.get("message").strip() != "", f"Expected a non-empty message in 200 response, got: {body.get('message')}"
    else:
        # For failure codes, expect error information in JSON
        if not any(k in body for k in ("error", "errors", "message", "status", "code")):
            raise AssertionError(f"Failure response JSON did not contain error fields: {body}")
        if "success" in body:
            assert not bool(body.get("success")), f"Expected success=false for failure response, got: {body.get('success')}"

if __name__ == "__main__":
    try:
        test_postapiauthlogoutinvalidsession()
        print("TC004 passed: logout returned an allowed response (200 or auth/failure) as expected.")
        sys.exit(0)
    except AssertionError as e:
        print(f"TC004 failed: {e}")
        sys.exit(1)
import os
import sys
import requests

BASE_URL = "http://localhost:8000"
LOGIN_PATH = "/api/auth/google"
LOGOUT_PATH = "/api/auth/logout"
PROTECTED_PATH = "/api/website"  # protected route that requires auth
TIMEOUT = 30


def test_post_api_auth_logout_valid_session():
    session = requests.Session()
    login_url = BASE_URL + LOGIN_PATH
    logout_url = BASE_URL + LOGOUT_PATH
    protected_url = BASE_URL + PROTECTED_PATH

    # Allow providing a real id token via env for CI runs; fallback to a placeholder
    id_token = os.environ.get("TEST_GOOGLE_ID_TOKEN", "test-id-token")

    logged_in = False
    try:
        # Attempt sign-in to obtain a session cookie
        login_payload = {"idToken": id_token}
        headers = {"Content-Type": "application/json"}

        resp_login = session.post(login_url, json=login_payload, headers=headers, timeout=TIMEOUT)
        # Expect 200 OK and a session cookie set
        assert resp_login is not None, "No response from login endpoint"
        assert resp_login.status_code == 200, f"Expected 200 from login, got {resp_login.status_code}, body: {resp_login.text}"

        # Ensure a cookie was set in the session
        cookie_count = len(session.cookies)
        assert cookie_count > 0, f"Expected at least one session cookie after login, found {cookie_count}"

        logged_in = True

        # Call logout with the valid session cookie
        resp_logout = session.post(logout_url, timeout=TIMEOUT)
        assert resp_logout is not None, "No response from logout endpoint"
        assert resp_logout.status_code == 200, f"Expected 200 from logout, got {resp_logout.status_code}, body: {resp_logout.text}"

        # Verify the server cleared the session cookie via Set-Cookie header or that client's cookie jar no longer has auth cookie
        set_cookie_header = resp_logout.headers.get("Set-Cookie", "") or resp_logout.headers.get("set-cookie", "")
        cleared_by_header = False
        if set_cookie_header:
            low = set_cookie_header.lower()
            if "max-age=0" in low or "expires=thu, 01 jan 1970" in low or "=;" in low:
                cleared_by_header = True

        cookies_after_logout = len(session.cookies)
        # requests updates cookies based on Set-Cookie in response; accept either header-based clearing or empty cookie jar
        assert cleared_by_header or cookies_after_logout == 0, (
            "Logout did not clear session cookie. "
            f"Set-Cookie header: {set_cookie_header!r}, cookies remaining: {cookies_after_logout}"
        )

        # Confirm protected route is no longer accessible (expect 401 or 403)
        resp_protected = session.get(protected_url, timeout=TIMEOUT)
        assert resp_protected is not None, "No response from protected endpoint after logout"
        assert resp_protected.status_code in (401, 403), (
            f"Expected unauthorized (401/403) accessing protected route after logout, "
            f"got {resp_protected.status_code}, body: {resp_protected.text}"
        )

        print("TC003 passed: logout returned 200 and session was cleared; protected route is unauthorized after logout.")
    except AssertionError:
        raise
    except Exception as e:
        raise
    finally:
        # Ensure session is cleaned up: attempt logout if still logged in
        try:
            if logged_in:
                # Use a short timeout for cleanup
                session.post(logout_url, timeout=5)
        except Exception:
            pass


if __name__ == "__main__":
    try:
        test_post_api_auth_logout_valid_session()
    except AssertionError as e:
        print("AssertionError:", e)
        sys.exit(1)
    except Exception as e:
        print("Error during test execution:", str(e))
        sys.exit(2)
    sys.exit(0)
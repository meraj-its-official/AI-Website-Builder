import requests
import sys
import time

BASE = "http://localhost:8000"
TIMEOUT = 30

def test_post_api_auth_logout_valid_session():
    session = requests.Session()
    headers = {"Content-Type": "application/json"}

    try:
        # 1) Optionally validate landing page if it exists
        try:
            r = session.get(f"{BASE}/", timeout=TIMEOUT)
        except Exception:
            r = None
        if r and r.status_code == 200:
            body = r.text.lower()
            assert ("context.ai" in body) or ("contex.ai" in body) or ("<div id=\"root\"" in r.text.lower()) or ("contex" in body), \
                "Landing page HTML does not contain expected identifiers"

        # 2) Sign in to create a valid session (requires a valid idToken in the environment)
        # Note: Replace TEST_VALID_ID_TOKEN with a real token when running against a live dev server.
        id_token_payload = {"idToken": "TEST_VALID_ID_TOKEN"}
        r = session.post(f"{BASE}/api/auth/google", json=id_token_payload, headers=headers, timeout=TIMEOUT)

        # If server responds asking for email, retry with an augmented payload (server-side implementation may require email)
        if r.status_code == 400:
            try:
                body_json = r.json()
            except Exception:
                body_json = {}
            message = "".join([str(v).lower() for v in (body_json.get("message") if isinstance(body_json, dict) else "")]) if body_json else ""
            if "email is required" in message or "email" in message:
                alt_payload = {"idToken": "TEST_VALID_ID_TOKEN", "email": "test@example.com", "name": "Test User"}
                r = session.post(f"{BASE}/api/auth/google", json=alt_payload, headers=headers, timeout=TIMEOUT)

        assert r.status_code == 200, f"Auth Google sign-in failed: {r.status_code} - {r.text}"
        # Ensure a session cookie was set
        cookies_after_signin = session.cookies.get_dict()
        assert cookies_after_signin, f"No cookies found after sign-in. Response headers: {r.headers}"

        # 3) Verify a protected route is accessible with the session (sanity check of session)
        r = session.get(f"{BASE}/api/website", timeout=TIMEOUT)
        assert r.status_code == 200, f"Protected route /api/website not accessible after sign-in: {r.status_code} {r.text}"

        # 4) Call logout with the valid session cookie
        r = session.post(f"{BASE}/api/auth/logout", timeout=TIMEOUT)
        assert r.status_code == 200, f"Logout did not return 200: {r.status_code} - {r.text}"

        # 5) Validate server cleared the session cookie (check Set-Cookie header or session cookies cleared)
        set_cookie_header = r.headers.get("Set-Cookie", "")
        cookies_after_logout = session.cookies.get_dict()
        cleared_via_header = False
        if set_cookie_header:
            sc_lower = set_cookie_header.lower()
            if ("max-age=0" in sc_lower) or ("expires=thu, 01 jan 1970" in sc_lower) or ("expires=" in sc_lower and ("1970" in sc_lower or "utc" in sc_lower)) or ("deleted" in sc_lower):
                cleared_via_header = True
        assert cleared_via_header or not cookies_after_logout, f"Session cookie was not cleared after logout. Set-Cookie: {set_cookie_header}, session cookies: {cookies_after_logout}"

        # 6) Verify protected route is no longer accessible without session cookie
        r = requests.get(f"{BASE}/api/website", timeout=TIMEOUT)
        assert r.status_code == 401, f"Protected route accessible without session after logout (expected 401): got {r.status_code} - {r.text}"

        print("TC003 passed: logout with valid session returned 200 and cleared session cookie.")

    except AssertionError:
        raise
    except Exception as exc:
        raise
    finally:
        # Best-effort cleanup: ensure server-side session is cleared for this session
        try:
            session.post(f"{BASE}/api/auth/logout", timeout=TIMEOUT)
        except Exception:
            pass


if __name__ == "__main__":
    try:
        test_post_api_auth_logout_valid_session()
    except AssertionError as e:
        print("Test failed:", e)
        sys.exit(1)
    except Exception as e:
        print("Error running test:", e)
        sys.exit(2)
    sys.exit(0)
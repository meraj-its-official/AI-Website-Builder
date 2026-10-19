import os
import time
import requests
from requests.exceptions import RequestException

BASE = "http://localhost:8000"
TIMEOUT = 30

def test_putapiwebsiteidvalidupdate():
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    website_id = None

    # 1) Validate landing page loads
    try:
        resp = session.get(f"{BASE}/", timeout=TIMEOUT)
    except RequestException as e:
        raise AssertionError(f"Landing page request failed: {e}")
    assert resp.status_code == 200, f"Landing page did not load (status {resp.status_code})"
    assert resp.text and len(resp.text) > 0, "Landing page returned empty body"

    # 2) Authenticate: prefer GOOGLE_ID_TOKEN, fallback to providing a session cookie via env
    id_token = os.environ.get("GOOGLE_ID_TOKEN")
    session_cookie = os.environ.get("TEST_SESSION_COOKIE")
    session_cookie_name = os.environ.get("SESSION_COOKIE_NAME", "connect.sid")

    if id_token:
        try:
            r = session.post(f"{BASE}/api/auth/google", json={"idToken": id_token}, timeout=TIMEOUT)
        except RequestException as e:
            raise AssertionError(f"Auth request failed: {e}")
        assert r.status_code == 200, f"Authentication with GOOGLE_ID_TOKEN failed: {r.status_code} {r.text}"
    elif session_cookie:
        # Set provided session cookie into the session for authenticated requests
        session.cookies.set(session_cookie_name, session_cookie, domain="localhost")
    else:
        raise RuntimeError("No authentication provided. Set GOOGLE_ID_TOKEN or TEST_SESSION_COOKIE environment variable.")

    # 3) Create a new website project to update (POST /api/website/generate)
    prompt = f"Automated test prompt for TC007 {int(time.time())}"
    try:
        r = session.post(f"{BASE}/api/website/generate", json={"prompt": prompt}, timeout=TIMEOUT)
    except RequestException as e:
        raise AssertionError(f"Create website request failed: {e}")
    assert r.status_code == 200, f"Website generation failed: {r.status_code} {r.text}"

    try:
        created = r.json()
    except ValueError:
        raise AssertionError("Website generation response is not valid JSON")

    # Extract website id from common fields
    website_id = created.get("id") or created.get("_id") or created.get("websiteId")
    if not website_id:
        # sometimes payload nested
        for candidate in ("data", "website", "result"):
            if isinstance(created.get(candidate), dict):
                website_id = created[candidate].get("id") or created[candidate].get("_id")
                if website_id:
                    break
    assert website_id, f"Could not determine website id from response: {created}"

    # Keep original code for potential restore
    original_code = created.get("code", "")

    # 4) Attempt to update with new code via PUT /api/website/:id
    updated_code = "<!doctype html><html><body><h1>TC007 - Updated</h1><p>Updated by automated test.</p></body></html>"
    try:
        put_resp = session.put(f"{BASE}/api/website/{website_id}", json={"code": updated_code}, timeout=TIMEOUT)
    except RequestException as e:
        # Ensure cleanup attempt
        try:
            session.delete(f"{BASE}/api/website/{website_id}", timeout=TIMEOUT)
        except Exception:
            pass
        raise AssertionError(f"PUT request failed: {e}")

    assert put_resp.status_code == 200, f"PUT did not return 200: {put_resp.status_code} {put_resp.text}"
    try:
        put_data = put_resp.json()
    except ValueError:
        raise AssertionError("PUT response is not valid JSON")

    # Validate that the returned resource reflects the updated code
    code_in_put = put_data.get("code") or (put_data.get("website") or {}).get("code")
    assert code_in_put is not None, f"PUT response does not include code field: {put_data}"
    assert updated_code in code_in_put, "PUT response code does not contain the updated HTML"

    # 5) GET the website to confirm persisted update
    try:
        get_resp = session.get(f"{BASE}/api/website/{website_id}", timeout=TIMEOUT)
    except RequestException as e:
        raise AssertionError(f"GET after PUT failed: {e}")
    assert get_resp.status_code == 200, f"GET after PUT returned {get_resp.status_code}: {get_resp.text}"
    try:
        get_data = get_resp.json()
    except ValueError:
        raise AssertionError("GET response is not valid JSON")
    code_in_get = get_data.get("code") or (get_data.get("website") or {}).get("code")
    assert code_in_get is not None, f"GET response missing code field: {get_data}"
    assert updated_code in code_in_get, "Persisted code does not match updated code"

    # 6) Cleanup: attempt to delete the created website (if API supports it). Use finally-like behavior below.
    try:
        del_resp = session.delete(f"{BASE}/api/website/{website_id}", timeout=TIMEOUT)
        # Accept common success codes or not-found (already deleted)
        if del_resp.status_code not in (200, 204, 404):
            # Not a hard failure for test, but surface unexpected response
            raise AssertionError(f"Unexpected delete response status: {del_resp.status_code} {del_resp.text}")
    except RequestException as e:
        # Non-fatal cleanup failure
        print(f"Cleanup DELETE request failed (non-fatal): {e}")

if __name__ == "__main__":
    test_putapiwebsiteidvalidupdate()
    print("TC007 completed successfully.")
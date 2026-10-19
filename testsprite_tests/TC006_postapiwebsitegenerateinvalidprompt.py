import os
import requests
import sys

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_postapiwebsitegenerateinvalidprompt():
    session = requests.Session()
    try:
        # 1) Validate landing page loads
        try:
            r = session.get(f"{BASE_URL}/", timeout=TIMEOUT)
        except requests.exceptions.RequestException as e:
            raise AssertionError(f"Failed to load landing page: {e}")
        assert r.status_code == 200, f"Landing page did not return 200 OK (status {r.status_code})"
        landing_ok = ("<!DOCTYPE html>" in r.text) or ("<div id=\"root\"" in r.text) or ("ConTex.ai" in r.text)
        assert landing_ok, "Landing page content does not look like the expected app HTML"

        # 2) Authenticate using a real Google identity token supplied via env var
        google_token = os.getenv("GOOGLE_ID_TOKEN")
        if not google_token:
            raise AssertionError("GOOGLE_ID_TOKEN environment variable is required for this test (set a valid Google/Firebase identity token)")

        auth_payload = {"idToken": google_token}
        try:
            auth_resp = session.post(f"{BASE_URL}/api/auth/google", json=auth_payload, timeout=TIMEOUT)
        except requests.exceptions.RequestException as e:
            raise AssertionError(f"Auth request failed: {e}")
        assert auth_resp.status_code == 200, f"Authentication failed (expected 200), got {auth_resp.status_code}: {auth_resp.text}"
        # ensure session cookie present
        assert session.cookies, "No cookies present after authentication; session cookie expected"

        # 3) Get current list of websites for the user
        try:
            list_before_resp = session.get(f"{BASE_URL}/api/website", timeout=TIMEOUT)
        except requests.exceptions.RequestException as e:
            raise AssertionError(f"GET /api/website failed: {e}")
        assert list_before_resp.status_code == 200, f"GET /api/website before generate failed with status {list_before_resp.status_code}: {list_before_resp.text}"
        try:
            list_before = list_before_resp.json()
        except ValueError:
            raise AssertionError("GET /api/website returned non-JSON response")
        assert isinstance(list_before, list), "Expected list of websites from GET /api/website"

        # 4) Attempt to generate a website with an invalid (empty) prompt
        invalid_payload = {"prompt": ""}
        try:
            gen_resp = session.post(f"{BASE_URL}/api/website/generate", json=invalid_payload, timeout=TIMEOUT)
        except requests.exceptions.RequestException as e:
            raise AssertionError(f"POST /api/website/generate failed: {e}")

        # Expect 400 invalid prompt
        assert gen_resp.status_code == 400, f"Expected 400 Invalid prompt, got {gen_resp.status_code}: {gen_resp.text}"
        # Try to assert error message indicates invalid prompt
        try:
            gen_json = gen_resp.json()
            # common keys: message, error, errors
            msg = ""
            if isinstance(gen_json, dict):
                msg = gen_json.get("message") or gen_json.get("error") or str(gen_json)
            else:
                msg = str(gen_json)
            assert ("invalid" in msg.lower()) or ("prompt" in msg.lower()), f"Unexpected error message for invalid prompt: {msg}"
        except ValueError:
            # non-JSON body is acceptable as long as status is 400
            pass

        # 5) Verify no project was created by comparing list before and after
        try:
            list_after_resp = session.get(f"{BASE_URL}/api/website", timeout=TIMEOUT)
        except requests.exceptions.RequestException as e:
            raise AssertionError(f"GET /api/website after generate failed: {e}")
        assert list_after_resp.status_code == 200, f"GET /api/website after generate failed with status {list_after_resp.status_code}: {list_after_resp.text}"
        try:
            list_after = list_after_resp.json()
        except ValueError:
            raise AssertionError("GET /api/website returned non-JSON response after generate")
        assert isinstance(list_after, list), "Expected list of websites from GET /api/website after generate"
        assert len(list_after) == len(list_before), "A project was created despite invalid prompt"

    finally:
        session.close()

if __name__ == "__main__":
    try:
        test_postapiwebsitegenerateinvalidprompt()
    except AssertionError as e:
        print(f"TEST FAILED: {e}")
        sys.exit(1)
    print("TEST PASSED: TC006 postapiwebsitegenerateinvalidprompt")
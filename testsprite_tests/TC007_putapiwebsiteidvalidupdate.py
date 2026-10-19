import requests
import sys
import time

BASE_URL = "http://localhost:8000"
TIMEOUT = 30  # seconds

def test_put_api_website_id_valid_update():
    session = requests.Session()
    created_website_id = None

    # Helper to extract id from website object
    def extract_id(obj):
        if not isinstance(obj, dict):
            return None
        for key in ("_id", "id", "uuid"):
            if key in obj:
                return obj[key]
        # sometimes API nests data
        if "website" in obj and isinstance(obj["website"], dict):
            for key in ("_id", "id"):
                if key in obj["website"]:
                    return obj["website"][key]
        return None

    try:
        # 1) Authenticate - attempt to sign in with a test idToken
        auth_payload = {"idToken": "TEST_ID_TOKEN"}
        resp = session.post(f"{BASE_URL}/api/auth/google", json=auth_payload, timeout=TIMEOUT)
        if resp.status_code != 200:
            raise AssertionError(f"Auth failed: expected 200, got {resp.status_code}, body: {resp.text}")
        # session cookie should be set in session automatically
        # 2) Create a new website resource to update
        generate_payload = {"prompt": "Test prompt for website update at " + str(int(time.time()))}
        resp = session.post(f"{BASE_URL}/api/website/generate", json=generate_payload, timeout=TIMEOUT)
        if resp.status_code != 200:
            raise AssertionError(f"Website generation failed: expected 200, got {resp.status_code}, body: {resp.text}")
        created = None
        try:
            created = resp.json()
        except ValueError:
            raise AssertionError(f"Website generation returned non-JSON: {resp.text}")
        created_website_id = extract_id(created)
        if not created_website_id:
            raise AssertionError(f"Could not determine created website id from response: {created}")

        # 3) PUT update the website's code
        updated_code = "<html><body><h1>Updated by test</h1></body></html>"
        put_payload = {"code": updated_code}
        resp = session.put(f"{BASE_URL}/api/website/{created_website_id}", json=put_payload, timeout=TIMEOUT)
        if resp.status_code != 200:
            raise AssertionError(f"PUT update failed: expected 200, got {resp.status_code}, body: {resp.text}")
        try:
            updated_resp = resp.json()
        except ValueError:
            raise AssertionError(f"PUT update returned non-JSON: {resp.text}")

        # Validate that returned Website data contains the updated code
        returned_code = None
        if isinstance(updated_resp, dict):
            # direct code field
            returned_code = updated_resp.get("code")
            # nested
            if returned_code is None and "website" in updated_resp and isinstance(updated_resp["website"], dict):
                returned_code = updated_resp["website"].get("code")
        assert returned_code == updated_code, f"Returned code does not match updated code. expected: {updated_code}, got: {returned_code}, full response: {updated_resp}"

        # 4) GET the website to confirm persisted update
        resp = session.get(f"{BASE_URL}/api/website/{created_website_id}", timeout=TIMEOUT)
        if resp.status_code != 200:
            raise AssertionError(f"GET after update failed: expected 200, got {resp.status_code}, body: {resp.text}")
        try:
            get_resp = resp.json()
        except ValueError:
            raise AssertionError(f"GET after update returned non-JSON: {resp.text}")

        fetched_code = None
        if isinstance(get_resp, dict):
            fetched_code = get_resp.get("code")
            if fetched_code is None and "website" in get_resp and isinstance(get_resp["website"], dict):
                fetched_code = get_resp["website"].get("code")
        assert fetched_code == updated_code, f"Persisted code does not match updated code. expected: {updated_code}, got: {fetched_code}, full response: {get_resp}"

        print("TC007 passed: PUT /api/website/:id updated and persisted code successfully.")

    finally:
        # Cleanup: attempt to delete the created website if possible
        if created_website_id:
            try:
                # Try DELETE endpoint if supported
                resp = session.delete(f"{BASE_URL}/api/website/{created_website_id}", timeout=TIMEOUT)
                # Accept 200/204/202/404 (404 means already gone)
                if resp.status_code not in (200, 202, 204, 404):
                    # If delete not allowed, attempt to revert code to empty as a fallback
                    try:
                        revert_payload = {"code": ""}
                        session.put(f"{BASE_URL}/api/website/{created_website_id}", json=revert_payload, timeout=TIMEOUT)
                    except Exception:
                        pass
            except Exception:
                pass

if __name__ == "__main__":
    try:
        test_put_api_website_id_valid_update()
    except AssertionError as e:
        print("TC007 failed:", e)
        sys.exit(1)
    except Exception as e:
        print("TC007 encountered an unexpected error:", e)
        sys.exit(2)
    sys.exit(0)
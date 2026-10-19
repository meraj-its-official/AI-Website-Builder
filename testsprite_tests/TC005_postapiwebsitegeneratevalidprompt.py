import os
import sys
import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_TC005_postapiwebsitegeneratevalidprompt():
    """
    Test POST /api/website/generate with a valid prompt and authenticated session.
    Flow:
    - Verify landing page loads (GET /)
    - Authenticate via POST /api/auth/google using env var TEST_GOOGLE_ID_TOKEN or GOOGLE_ID_TOKEN
    - POST /api/website/generate with a valid prompt
    - Verify response is 200 and contains a saved Website project id
    - GET /api/website/:id to verify stored project
    - GET /api/website to verify project appears in listing
    - Cleanup: attempt to DELETE /api/website/:id (if supported) in finally
    """
    token = os.getenv("TEST_GOOGLE_ID_TOKEN") or os.getenv("GOOGLE_ID_TOKEN")
    assert token, (
        "Google ID token not provided. Set TEST_GOOGLE_ID_TOKEN or GOOGLE_ID_TOKEN environment variable "
        "with a valid Firebase/Google identity token for testing."
    )

    session = requests.Session()
    created_id = None

    try:
        # 1) Landing page loads
        try:
            r = session.get(f"{BASE_URL}/", timeout=TIMEOUT)
        except requests.RequestException as e:
            raise AssertionError(f"Failed to GET landing page: {e}")
        assert r.status_code == 200, f"Landing page did not load successfully, status: {r.status_code}"
        assert len(r.content) > 0, "Landing page returned empty content"

        # 2) Authenticate with Google ID token
        auth_payload = {"idToken": token}
        try:
            r = session.post(f"{BASE_URL}/api/auth/google", json=auth_payload, timeout=TIMEOUT)
        except requests.RequestException as e:
            raise AssertionError(f"Auth request failed: {e}")
        assert r.status_code == 200, f"Authentication failed, expected 200 got {r.status_code}"
        # ensure session cookie is set (common cookie names vary; just ensure some cookie exists)
        cookies_after_auth = session.cookies.items()
        assert len(list(cookies_after_auth)) > 0, "No session cookies set after authentication"

        # 3) POST /api/website/generate with a valid prompt
        prompt_text = (
            "Generate a clean one-page portfolio for a freelance photographer with hero image, "
            "about section, gallery grid, and contact form."
        )
        gen_payload = {"prompt": prompt_text}
        try:
            r = session.post(f"{BASE_URL}/api/website/generate", json=gen_payload, timeout=TIMEOUT)
        except requests.RequestException as e:
            raise AssertionError(f"Website generate request failed: {e}")
        assert r.status_code == 200, f"Website generation failed, expected 200 got {r.status_code}"

        try:
            gen_json = r.json()
        except ValueError:
            raise AssertionError("Website generate response is not valid JSON")

        # Determine project ID in response
        created_id = None
        if isinstance(gen_json, dict):
            # common id fields
            created_id = gen_json.get("id") or gen_json.get("_id") or gen_json.get("projectId")
            # maybe wrapped in data
            if not created_id and "data" in gen_json and isinstance(gen_json["data"], dict):
                created_id = (
                    gen_json["data"].get("id")
                    or gen_json["data"].get("_id")
                    or gen_json["data"].get("projectId")
                )
        assert created_id, f"Generated project response did not contain an id. Response: {gen_json}"

        # Ensure generated project contains code or html content
        code_present = False
        for key in ("code", "html", "content"):
            if key in gen_json and isinstance(gen_json[key], str) and gen_json[key].strip():
                code_present = True
                break
            if "data" in gen_json and isinstance(gen_json["data"], dict):
                val = gen_json["data"].get(key)
                if isinstance(val, str) and val.strip():
                    code_present = True
                    break
        assert code_present, "Generated project did not include website code/html in response"

        # 4) GET /api/website/:id to fetch stored project
        try:
            r = session.get(f"{BASE_URL}/api/website/{created_id}", timeout=TIMEOUT)
        except requests.RequestException as e:
            raise AssertionError(f"GET project by id failed: {e}")
        assert r.status_code == 200, f"Fetching created project failed, expected 200 got {r.status_code}"
        try:
            project_json = r.json()
        except ValueError:
            raise AssertionError("GET project response is not valid JSON")
        # basic checks on returned project
        returned_id = (
            project_json.get("id") or project_json.get("_id") or (project_json.get("data") or {}).get("_id")
        )
        assert returned_id and str(returned_id) == str(created_id), "Fetched project id does not match created id"

        # 5) GET /api/website to ensure listing includes created project
        try:
            r = session.get(f"{BASE_URL}/api/website", timeout=TIMEOUT)
        except requests.RequestException as e:
            raise AssertionError(f"GET website listing failed: {e}")
        assert r.status_code == 200, f"Listing websites failed, expected 200 got {r.status_code}"
        try:
            list_json = r.json()
        except ValueError:
            raise AssertionError("Website listing response is not valid JSON")
        # Expect an array of websites
        assert isinstance(list_json, list) or (
            isinstance(list_json, dict) and isinstance(list_json.get("data"), list)
        ), "Website listing did not return an array"
        found = False
        if isinstance(list_json, list):
            for item in list_json:
                if (item.get("id") or item.get("_id") or item.get("projectId")) and str(
                    (item.get("id") or item.get("_id") or item.get("projectId"))
                ) == str(created_id):
                    found = True
                    break
        else:
            for item in list_json.get("data", []):
                if (item.get("id") or item.get("_id") or item.get("projectId")) and str(
                    (item.get("id") or item.get("_id") or item.get("projectId"))
                ) == str(created_id):
                    found = True
                    break
        assert found, "Created project not found in website listing for the authenticated user"

        print("TC005 passed: Website generated, stored, and retrievable for authenticated user.")

    finally:
        # Cleanup: attempt to delete the created project if possible
        if created_id:
            try:
                r = session.delete(f"{BASE_URL}/api/website/{created_id}", timeout=TIMEOUT)
                # Accept 200, 204 as success; if not allowed, do not fail the test during cleanup
                if r.status_code in (200, 204):
                    print(f"Cleanup: Deleted project {created_id}")
                else:
                    print(f"Cleanup: DELETE returned status {r.status_code} for project {created_id}; response: {r.text}")
            except requests.RequestException as e:
                print(f"Cleanup: Failed to DELETE project {created_id}: {e}")


if __name__ == "__main__":
    try:
        test_TC005_postapiwebsitegeneratevalidprompt()
    except AssertionError as e:
        print(f"TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
        sys.exit(2)
    else:
        print("TEST COMPLETED SUCCESSFULLY")
        sys.exit(0)
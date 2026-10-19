import os
import sys
import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30  # seconds

def test_post_api_website_generate_valid_prompt():
    """
    TC005: Test POST /api/website/generate with a valid prompt and authenticated session
    Ensures a 200 response and a saved Website project is returned, then cleans up.
    """
    session = requests.Session()
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    # Obtain a Google/Firebase identity token from environment for test auth
    id_token = os.environ.get("TEST_GOOGLE_ID_TOKEN")
    assert id_token, "Environment variable TEST_GOOGLE_ID_TOKEN must be set to run this test."

    auth_url = f"{BASE_URL}/api/auth/google"
    generate_url = f"{BASE_URL}/api/website/generate"
    logout_url = f"{BASE_URL}/api/auth/logout"

    created_id = None

    try:
        # 1) Authenticate: POST /api/auth/google
        auth_payload = {"idToken": id_token}
        try:
            auth_resp = session.post(auth_url, json=auth_payload, headers=headers, timeout=TIMEOUT)
        except requests.RequestException as e:
            raise AssertionError(f"Auth request to {auth_url} failed: {e}")

        assert auth_resp is not None, "No response from auth endpoint."
        if auth_resp.status_code != 200:
            # try to include response body for debug
            body = None
            try:
                body = auth_resp.json()
            except Exception:
                body = auth_resp.text
            raise AssertionError(f"Authentication failed. Expected 200, got {auth_resp.status_code}. Response: {body}")

        # Check that session cookie(s) were set
        assert session.cookies, "No session cookies set after authentication; auth may not have created a session."

        # 2) POST /api/website/generate with a valid prompt
        prompt_text = "Create a simple responsive landing page for a fictional coffee shop called 'Morning Brew' with header, menu section, contact form, and footer."
        generate_payload = {"prompt": prompt_text}
        try:
            gen_resp = session.post(generate_url, json=generate_payload, headers=headers, timeout=TIMEOUT)
        except requests.RequestException as e:
            raise AssertionError(f"Website generate request to {generate_url} failed: {e}")

        assert gen_resp is not None, "No response from website generate endpoint."
        # Expect 200 with created Website project
        if gen_resp.status_code != 200:
            body = None
            try:
                body = gen_resp.json()
            except Exception:
                body = gen_resp.text
            raise AssertionError(f"Website generation failed. Expected 200, got {gen_resp.status_code}. Response: {body}")

        try:
            gen_data = gen_resp.json()
        except ValueError:
            raise AssertionError("Website generate response is not valid JSON.")

        # Extract created project ID from common fields
        created_id = None
        if isinstance(gen_data, dict):
            for key in ("id", "_id", "projectId", "websiteId", "uid"):
                if key in gen_data and gen_data[key]:
                    created_id = str(gen_data[key])
                    break
            # sometimes API nests the project under 'website' or 'data'
            if not created_id:
                for container in ("website", "data", "project"):
                    if container in gen_data and isinstance(gen_data[container], dict):
                        for key in ("id", "_id", "projectId", "websiteId"):
                            if key in gen_data[container] and gen_data[container][key]:
                                created_id = str(gen_data[container][key])
                                break
                        if created_id:
                            break

        assert created_id, f"Could not extract created project ID from response: {gen_data}"

        # 3) GET /api/website/:id to verify it was saved
        get_url = f"{BASE_URL}/api/website/{created_id}"
        try:
            get_resp = session.get(get_url, headers=headers, timeout=TIMEOUT)
        except requests.RequestException as e:
            raise AssertionError(f"GET project request to {get_url} failed: {e}")

        assert get_resp is not None, "No response from GET project endpoint."
        if get_resp.status_code != 200:
            body = None
            try:
                body = get_resp.json()
            except Exception:
                body = get_resp.text
            raise AssertionError(f"Fetching created project failed. Expected 200, got {get_resp.status_code}. Response: {body}")

        try:
            get_data = get_resp.json()
        except ValueError:
            raise AssertionError("GET project response is not valid JSON.")

        # Basic validation: returned project should contain same id and some code/content/title
        found_id = None
        if isinstance(get_data, dict):
            for key in ("id", "_id", "projectId", "websiteId"):
                if key in get_data and get_data[key]:
                    found_id = str(get_data[key])
                    break
            # check nested
            if not found_id:
                for container in ("website", "data", "project"):
                    if container in get_data and isinstance(get_data[container], dict):
                        for key in ("id", "_id", "projectId", "websiteId"):
                            if key in get_data[container] and get_data[container][key]:
                                found_id = str(get_data[container][key])
                                break
                        if found_id:
                            break

        assert found_id, f"Could not find an ID field in GET project response: {get_data}"
        assert found_id == created_id, f"Fetched project ID ({found_id}) does not match created ID ({created_id})."

        # Expect at least some content like code/html/title in returned project
        has_content = False
        for content_field in ("code", "html", "title", "slug", "name", "content"):
            if isinstance(get_data, dict):
                if content_field in get_data and get_data[content_field]:
                    has_content = True
                    break
                # nested
                for container in ("website", "data", "project"):
                    if container in get_data and isinstance(get_data[container], dict) and get_data[container].get(content_field):
                        has_content = True
                        break
                if has_content:
                    break

        assert has_content, f"Returned project does not contain expected content fields. Response: {get_data}"

    finally:
        # Cleanup: attempt to delete the created project if we were able to create one
        if created_id:
            delete_url = f"{BASE_URL}/api/website/{created_id}"
            try:
                # Some APIs support DELETE; attempt it and tolerate 404/403 if deletion not permitted
                del_resp = session.delete(delete_url, headers=headers, timeout=TIMEOUT)
                # Accept 200/204 as successful deletes; ignore 404/403 but log via assertion message only on unexpected codes
                if del_resp.status_code not in (200, 204, 202, 404, 403):
                    try:
                        body = del_resp.json()
                    except Exception:
                        body = del_resp.text
                    print(f"Warning: unexpected status from DELETE {delete_url}: {del_resp.status_code}. Response: {body}", file=sys.stderr)
            except requests.RequestException as e:
                print(f"Warning: DELETE request to {delete_url} failed: {e}", file=sys.stderr)

        # Attempt to logout to clear session cookie
        try:
            lo_resp = session.post(logout_url, headers=headers, timeout=TIMEOUT)
            # logout may require auth; accept both success and non-2xx but warn on failure
            if lo_resp.status_code != 200:
                try:
                    body = lo_resp.json()
                except Exception:
                    body = lo_resp.text
                print(f"Warning: logout returned status {lo_resp.status_code}. Response: {body}", file=sys.stderr)
        except requests.RequestException as e:
            print(f"Warning: logout request failed: {e}", file=sys.stderr)

if __name__ == "__main__":
    test_post_api_website_generate_valid_prompt()
    print("TC005 passed.")
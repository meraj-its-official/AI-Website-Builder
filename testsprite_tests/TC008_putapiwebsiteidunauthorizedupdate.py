import os
import requests
import sys
import json

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def login_with_token(id_token):
    url = f"{BASE_URL}/api/auth/google"
    try:
        resp = requests.post(url, json={"idToken": id_token}, timeout=TIMEOUT)
    except Exception as e:
        raise RuntimeError(f"Auth request failed: {e}")
    if resp.status_code != 200:
        raise RuntimeError(f"Auth failed with status {resp.status_code}: {resp.text}")
    # Build cookie header string from response cookies
    cookie_header = "; ".join([f"{k}={v}" for k, v in resp.cookies.items()])
    return cookie_header

def cookie_header_from_env(cookie_str):
    # Accept cookie string as-is (e.g. "connect.sid=abc; other=xyz")
    return cookie_str.strip()

def create_website(prompt, cookie_header):
    url = f"{BASE_URL}/api/website/generate"
    headers = {"Content-Type": "application/json"}
    if cookie_header:
        headers["Cookie"] = cookie_header
    try:
        resp = requests.post(url, json={"prompt": prompt}, headers=headers, timeout=TIMEOUT)
    except Exception as e:
        raise RuntimeError(f"Create website request failed: {e}")
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to create website: status {resp.status_code}, body: {resp.text}")
    try:
        data = resp.json()
    except Exception:
        raise RuntimeError(f"Create website did not return JSON: {resp.text}")
    # Try common id fields
    project_id = data.get("_id") or data.get("id") or data.get("projectId") or (data.get("website") and (data["website"].get("_id") or data["website"].get("id")))
    if not project_id:
        raise RuntimeError(f"Could not determine created project ID from response: {json.dumps(data)}")
    # Determine code if present
    code = data.get("code") or (data.get("website") and data["website"].get("code")) or ""
    return project_id, code, data

def get_website(project_id, cookie_header):
    url = f"{BASE_URL}/api/website/{project_id}"
    headers = {}
    if cookie_header:
        headers["Cookie"] = cookie_header
    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)
    except Exception as e:
        raise RuntimeError(f"Get website request failed: {e}")
    if resp.status_code == 200:
        try:
            return resp.json()
        except Exception:
            raise RuntimeError(f"GET website returned non-JSON: {resp.text}")
    else:
        return {"_status_code": resp.status_code, "_body": resp.text}

def delete_website(project_id, cookie_header):
    url = f"{BASE_URL}/api/website/{project_id}"
    headers = {}
    if cookie_header:
        headers["Cookie"] = cookie_header
    try:
        resp = requests.delete(url, headers=headers, timeout=TIMEOUT)
    except Exception as e:
        # If delete request fails at network level, just log and return
        return {"error": str(e)}
    return {"status_code": resp.status_code, "body": resp.text}

def test_put_api_website_id_unauthorized_update():
    """
    TC008: Test PUT /api/website/:id with a project ID owned by another user or invalid session
    to verify it returns 403 unauthorized or 404 not found and does not save changes.
    """
    # Environment helpers:
    # TEST_AUTH_TOKEN -> id token to authenticate as owner (preferred)
    # TEST_SESSION_COOKIE -> raw cookie string for owner session (e.g. "connect.sid=...")
    # OTHER_SESSION_COOKIE -> raw cookie string to simulate a different user session (optional)
    # EXISTING_WEBSITE_ID -> if provided, use this project id instead of creating one
    owner_cookie = None
    other_cookie = None
    project_id = os.environ.get("EXISTING_WEBSITE_ID")

    try:
        # Prepare owner session cookie
        if os.environ.get("TEST_SESSION_COOKIE"):
            owner_cookie = cookie_header_from_env(os.environ["TEST_SESSION_COOKIE"])
        elif os.environ.get("TEST_AUTH_TOKEN"):
            owner_cookie = login_with_token(os.environ["TEST_AUTH_TOKEN"])
        else:
            # If we plan to use an existing website id, try to get its owner cookie from env
            if project_id and os.environ.get("EXISTING_WEBSITE_OWNER_COOKIE"):
                owner_cookie = cookie_header_from_env(os.environ["EXISTING_WEBSITE_OWNER_COOKIE"])
            else:
                raise RuntimeError("No owner authentication provided. Set TEST_AUTH_TOKEN or TEST_SESSION_COOKIE or provide EXISTING_WEBSITE_ID with EXISTING_WEBSITE_OWNER_COOKIE.")

        # Prepare other (unauthorized) session cookie if provided
        if os.environ.get("OTHER_SESSION_COOKIE"):
            other_cookie = cookie_header_from_env(os.environ["OTHER_SESSION_COOKIE"])

        created_here = False
        original_code = ""

        # Create a website project if no existing id provided
        if not project_id:
            project_id, original_code, created_response = create_website(
                prompt="TestSprite: unauthorized update test prompt",
                cookie_header=owner_cookie
            )
            created_here = True
            # If the created response contains nested website object, try to extract code
            if not original_code:
                # try nested fields
                if isinstance(created_response, dict):
                    original_code = created_response.get("code") or (created_response.get("website") and created_response["website"].get("code")) or ""
        else:
            # Fetch existing project to record original code
            fetched = get_website(project_id, owner_cookie)
            if fetched.get("_status_code"):
                raise RuntimeError(f"Could not fetch existing website {project_id} with owner cookie: status {fetched['_status_code']}, body: {fetched['_body']}")
            original_code = fetched.get("code", "") or (fetched.get("website") and fetched["website"].get("code")) or ""
        # Ensure we have a project id
        assert project_id, "Project ID must be available for the test."

        # Attempt unauthorized update: prefer using OTHER_SESSION_COOKIE if provided to simulate another user,
        # otherwise attempt with no session (no Cookie header)
        url_put = f"{BASE_URL}/api/website/{project_id}"
        headers_put = {"Content-Type": "application/json"}
        if other_cookie:
            headers_put["Cookie"] = other_cookie
        # payload with attempted change
        new_code = "<!-- malicious change -->"
        try:
            resp_put = requests.put(url_put, json={"code": new_code}, headers=headers_put, timeout=TIMEOUT)
        except Exception as e:
            raise RuntimeError(f"Unauthorized PUT request failed: {e}")

        # The system is expected to prevent unauthorized updates. Accept 403 or 404 (or 401 in some setups).
        allowed_statuses = {403, 404}
        # Be slightly permissive to include 401 as well, but prefer 403/404 per PRD.
        allowed_statuses_with_401 = allowed_statuses.union({401})
        assert resp_put.status_code in allowed_statuses_with_401, (
            f"Expected unauthorized response (403/404/401) from PUT, got {resp_put.status_code}: {resp_put.text}"
        )

        # Now fetch the project with the owner session and ensure the code was not changed
        fetched_after = get_website(project_id, owner_cookie)
        if fetched_after.get("_status_code"):
            # If owner cannot fetch the project anymore, that's unexpected for this test
            raise AssertionError(f"Owner could not fetch project after unauthorized PUT: status {fetched_after['_status_code']}, body: {fetched_after['_body']}")

        fetched_code = fetched_after.get("code") or (fetched_after.get("website") and fetched_after["website"].get("code")) or ""
        assert fetched_code == original_code, (
            "Project code was changed by an unauthorized update attempt. "
            f"Original: {original_code!r}, After attempt: {fetched_code!r}"
        )

        print("TC008 passed: unauthorized PUT was rejected and changes were not saved.")
    finally:
        # Cleanup: if we created the project, try to delete it using owner_cookie
        if 'project_id' in locals() and project_id and created_here:
            try:
                result = delete_website(project_id, owner_cookie)
                # We won't fail the test due to cleanup issues, but log if deletion did not appear successful
                status = result.get("status_code") if isinstance(result, dict) else None
                if status and status not in (200, 202, 204):
                    print(f"Cleanup warning: delete returned status {status}, body: {result.get('body')}")
            except Exception as e:
                print(f"Cleanup error: {e}")

if __name__ == "__main__":
    try:
        test_put_api_website_id_unauthorized_update()
    except AssertionError as ae:
        print(f"AssertionError: {ae}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(2)
import os
import sys
import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_post_api_website_generate_invalid_prompt():
    """
    TC006 - postapiwebsitegenerateinvalidprompt
    Test POST /api/website/generate with an empty or invalid prompt to verify it returns 400 invalid prompt
    and does not create a project.
    """
    google_token = os.getenv("GOOGLE_ID_TOKEN")
    if not google_token:
        raise AssertionError(
            "Environment variable GOOGLE_ID_TOKEN is required for authentication. Set it to a valid test Google/Firebase identity token."
        )

    session = requests.Session()
    logged_in = False

    try:
        # 1) Authenticate via POST /api/auth/google
        auth_payload = {"idToken": google_token}
        try:
            resp = session.post(f"{BASE_URL}/api/auth/google", json=auth_payload, timeout=TIMEOUT)
        except requests.RequestException as e:
            raise AssertionError(f"Auth request failed: {e}")

        if resp.status_code != 200:
            raise AssertionError(f"Authentication failed: expected status 200, got {resp.status_code}, body: {resp.text}")

        # Consider login successful if status 200
        logged_in = True

        # 2) Get current list of websites for the user
        try:
            resp_before = session.get(f"{BASE_URL}/api/website", timeout=TIMEOUT)
        except requests.RequestException as e:
            raise AssertionError(f"GET /api/website failed: {e}")

        if resp_before.status_code != 200:
            raise AssertionError(f"Failed to list websites before test: expected 200, got {resp_before.status_code}, body: {resp_before.text}")

        try:
            websites_before = resp_before.json()
        except ValueError:
            raise AssertionError(f"GET /api/website returned non-JSON body: {resp_before.text}")

        if not isinstance(websites_before, list):
            raise AssertionError(f"GET /api/website did not return a list: {websites_before}")

        count_before = len(websites_before)

        # 3) Attempt to generate a website with an invalid/empty prompt
        generate_payload = {"prompt": ""}  # empty prompt is invalid per PRD
        try:
            resp_generate = session.post(f"{BASE_URL}/api/website/generate", json=generate_payload, timeout=TIMEOUT)
        except requests.RequestException as e:
            raise AssertionError(f"POST /api/website/generate request failed: {e}")

        # Expect 400 invalid prompt
        if resp_generate.status_code == 200:
            # Unexpected success: parse returned project and fail the test
            try:
                project = resp_generate.json()
            except ValueError:
                project = resp_generate.text
            raise AssertionError(f"Expected 400 for invalid prompt but got 200 with body: {project}")

        if resp_generate.status_code != 400:
            raise AssertionError(
                f"Expected 400 Invalid prompt response, got {resp_generate.status_code}. Body: {resp_generate.text}"
            )

        # Optionally check for message indicating invalid prompt
        try:
            body = resp_generate.json()
            # Accept either {'error': 'Invalid prompt'} or {'message': 'Invalid prompt'} or similar
            msg = None
            if isinstance(body, dict):
                msg = body.get("error") or body.get("message") or body.get("detail")
            if msg:
                assert "invalid" in msg.lower() or "prompt" in msg.lower(), f"400 response body does not indicate invalid prompt: {body}"
        except ValueError:
            # Non-JSON 400 body is acceptable as long as status is 400
            pass

        # 4) Ensure no new project was created by re-listing and checking count unchanged
        try:
            resp_after = session.get(f"{BASE_URL}/api/website", timeout=TIMEOUT)
        except requests.RequestException as e:
            raise AssertionError(f"GET /api/website after generate failed: {e}")

        if resp_after.status_code != 200:
            raise AssertionError(f"Failed to list websites after test: expected 200, got {resp_after.status_code}, body: {resp_after.text}")

        try:
            websites_after = resp_after.json()
        except ValueError:
            raise AssertionError(f"GET /api/website returned non-JSON body after test: {resp_after.text}")

        if not isinstance(websites_after, list):
            raise AssertionError(f"GET /api/website did not return a list after test: {websites_after}")

        count_after = len(websites_after)

        assert count_after == count_before, f"Project count changed after invalid generate: before={count_before}, after={count_after}"

        print("TC006 passed: POST /api/website/generate with invalid prompt returned 400 and no project was created.")

    finally:
        # Attempt to logout if we logged in
        if logged_in:
            try:
                session.post(f"{BASE_URL}/api/auth/logout", timeout=TIMEOUT)
            except Exception:
                # best-effort logout; do not mask test result
                pass


if __name__ == "__main__":
    test_post_api_website_generate_invalid_prompt()
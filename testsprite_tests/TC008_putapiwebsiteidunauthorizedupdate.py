import requests
import uuid
import sys
import traceback
import json

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_putapiwebsiteidunauthorizedupdate():
    session = requests.Session()
    created_id = None
    created = False
    original_code = None

    try:
        # 1) Validate landing page loads
        try:
            r = session.get(f"{BASE_URL}/", timeout=TIMEOUT)
            assert r.status_code == 200, f"Landing page did not return 200, got {r.status_code}"
            assert "<" in r.text[:200] or "html" in r.text.lower()[:200], "Landing page content looks unexpected"
        except Exception as e:
            raise AssertionError(f"Landing page check failed: {e}")

        headers = {"Content-Type": "application/json"}

        # 2) Try to create a new website project (no auth). If server requires auth, this will likely fail.
        prompt_payload = {"prompt": "Test project for unauthorized update - " + str(uuid.uuid4())}
        try:
            r = session.post(f"{BASE_URL}/api/website/generate", headers=headers, data=json.dumps(prompt_payload), timeout=TIMEOUT)
        except Exception as e:
            raise AssertionError(f"Request to create project failed: {e}")

        if r.status_code == 200:
            # Attempt to extract an ID from response
            try:
                body = r.json()
            except Exception:
                raise AssertionError("Create project returned 200 but response is not JSON")

            # Common id fields: id, _id
            created_id = body.get("id") or body.get("_id") or (body.get("website") or {}).get("_id") or (body.get("data") or {}).get("id")
            if not created_id:
                # try nested search
                for v in body.values():
                    if isinstance(v, dict):
                        if v.get("id") or v.get("_id"):
                            created_id = v.get("id") or v.get("_id")
                            break

            if not created_id:
                # If no id found but response looks like a website, fail the test since we can't cleanup/verify
                raise AssertionError("Create project returned 200 but no project ID found in response")

            created = True

            # Try to capture original code if present
            original_code = body.get("code") or (body.get("website") or {}).get("code") or (body.get("data") or {}).get("code")

        else:
            # Creation failed (likely due to authentication). We'll proceed using a random non-existent ID to test unauthorized update.
            created_id = str(uuid.uuid4())

        # 3) Attempt unauthorized update: no auth/session cookie for updating
        update_payload = {"code": "<html><body>UNAUTHORIZED UPDATE " + str(uuid.uuid4()) + "</body></html>"}
        # Use a fresh session that has no cookies to simulate invalid session / other-user
        anon_session = requests.Session()
        try:
            r_update = anon_session.put(f"{BASE_URL}/api/website/{created_id}", headers=headers, data=json.dumps(update_payload), timeout=TIMEOUT)
        except Exception as e:
            raise AssertionError(f"Unauthorized update request failed: {e}")

        # Acceptable responses: 403 Unauthorized (ownership), 404 Not Found (project not found), or 401 Unauthorized (no valid session)
        if r_update.status_code in (401, 403, 404):
            # PASS for status code expectation
            pass
        else:
            # If server returned 200, it's a failure — changes must not be saved under unauthorized update
            if r_update.status_code == 200:
                # If update succeeded despite missing/invalid session, fail
                raise AssertionError("PUT /api/website/:id succeeded without proper authorization (status 200). This should not happen.")
            else:
                raise AssertionError(f"PUT /api/website/:id returned unexpected status {r_update.status_code}, expected one of [401,403,404]")

        # 4) Verify that changes were not saved:
        # If we created the resource and can GET it (without auth or with same session), ensure code not changed.
        if created:
            # Try GET with anon_session first (likely will be unauthorized). If it fails with auth error, try the original session that created it.
            got_project = None
            get_status = None
            try:
                r_get = anon_session.get(f"{BASE_URL}/api/website/{created_id}", timeout=TIMEOUT)
                get_status = r_get.status_code
                if r_get.status_code == 200:
                    try:
                        got_project = r_get.json()
                    except:
                        got_project = None
            except Exception:
                get_status = None

            if got_project is None:
                # Try with the session that created it (if creation was done without auth, it's the same; but try anyway)
                try:
                    r_get2 = session.get(f"{BASE_URL}/api/website/{created_id}", timeout=TIMEOUT)
                    get_status = r_get2.status_code
                    if r_get2.status_code == 200:
                        try:
                            got_project = r_get2.json()
                        except:
                            got_project = None
                except Exception:
                    get_status = None

            if got_project:
                # Extract code
                fetched_code = got_project.get("code") or (got_project.get("website") or {}).get("code") or (got_project.get("data") or {}).get("code")
                # If we have original_code captured from creation, ensure it wasn't changed to the unauthorized update payload
                if fetched_code is not None:
                    assert fetched_code != update_payload["code"], "Unauthorized update appears to have been saved — code matches the attempted unauthorized update"
                else:
                    # If no code field, just ensure that the update payload is not present anywhere in the serialized object
                    serialized = json.dumps(got_project)
                    assert update_payload["code"] not in serialized, "Unauthorized update payload found in project data"
            else:
                # Unable to fetch project (likely due to auth) — this is acceptable for unauthorized scenario
                pass

        # If we reach here, test passed
        print("TC008 passed: unauthorized/invalid-session PUT returned expected error and no unauthorized changes were observed where verifiable.")

    except AssertionError as e:
        print("TC008 failed:", e)
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print("TC008 encountered an unexpected error:", e)
        traceback.print_exc()
        sys.exit(2)
    finally:
        # Cleanup: attempt to delete created resource if any (best-effort). Use the session that created it.
        if created and created_id:
            try:
                # Attempt delete; accept 200/204/202/401/403/404 as non-fatal in cleanup
                r_del = session.delete(f"{BASE_URL}/api/website/{created_id}", timeout=TIMEOUT)
                if r_del.status_code not in (200, 204, 202, 401, 403, 404):
                    print(f"Cleanup: unexpected delete status {r_del.status_code}")
            except Exception as e:
                # Log cleanup error but do not fail the test because primary assertions already ran
                print(f"Cleanup: failed to delete project {created_id}: {e}")

if __name__ == "__main__":
    test_putapiwebsiteidunauthorizedupdate()
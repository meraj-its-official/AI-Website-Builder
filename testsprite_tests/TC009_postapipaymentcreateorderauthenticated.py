import os
import sys
import requests
from requests.exceptions import RequestException

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_post_api_payment_create_order_authenticated():
    session = requests.Session()
    session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})

    # Helper to fail with clear message
    def fail(msg):
        session.close()
        raise AssertionError(msg)

    try:
        # 1) Retrieve available plans (no auth required)
        try:
            resp = session.get(f"{BASE_URL}/api/payment/plans", timeout=TIMEOUT)
        except RequestException as e:
            fail(f"Failed to GET /api/payment/plans: {e}")
        assert resp.status_code == 200, f"GET /api/payment/plans returned {resp.status_code}, expected 200"
        plans = None
        try:
            plans = resp.json()
        except ValueError:
            fail("GET /api/payment/plans did not return valid JSON")
        assert isinstance(plans, list) and len(plans) > 0, "Expected a non-empty list of plans from /api/payment/plans"

        # determine a planId from the first plan using common keys
        first_plan = plans[0]
        plan_id = None
        for key in ("id", "_id", "planId", "plan_id"):
            if key in first_plan:
                plan_id = first_plan[key]
                break
        if plan_id is None:
            # maybe plan is a simple string id
            if isinstance(first_plan, str):
                plan_id = first_plan
            else:
                fail(f"Could not determine planId from plan object: {first_plan}")

        # 2) Authenticate using a Google/Firebase identity token provided via env var
        id_token = os.environ.get("TEST_GOOGLE_ID_TOKEN")
        if not id_token:
            fail("Environment variable TEST_GOOGLE_ID_TOKEN is required for authenticated tests but not set")

        auth_payload = {"idToken": id_token}
        try:
            auth_resp = session.post(f"{BASE_URL}/api/auth/google", json=auth_payload, timeout=TIMEOUT)
        except RequestException as e:
            fail(f"Failed to POST /api/auth/google: {e}")
        assert auth_resp.status_code == 200, f"POST /api/auth/google returned {auth_resp.status_code}, expected 200"

        # Optional: verify protected route to confirm session is active
        try:
            me_resp = session.get(f"{BASE_URL}/api/user/me", timeout=TIMEOUT)
        except RequestException:
            # If /api/user/me is not available, skip this verification but keep authenticated session
            me_resp = None
        if me_resp is not None:
            assert me_resp.status_code == 200, f"Expected 200 from /api/user/me after auth, got {me_resp.status_code}"

        # 3) Create order for selected plan
        create_payload = {"planId": plan_id}
        try:
            order_resp = session.post(f"{BASE_URL}/api/payment/create-order", json=create_payload, timeout=TIMEOUT)
        except RequestException as e:
            fail(f"Failed to POST /api/payment/create-order: {e}")

        assert order_resp.status_code == 200, f"POST /api/payment/create-order returned {order_resp.status_code}, expected 200"
        try:
            order_json = order_resp.json()
        except ValueError:
            fail("POST /api/payment/create-order did not return valid JSON")

        # Validate that server returned order information. Accept common keys.
        order_obj = None
        # Response might be the order object directly or wrapped under "order"
        if isinstance(order_json, dict):
            if "order" in order_json and isinstance(order_json["order"], dict):
                order_obj = order_json["order"]
            else:
                order_obj = order_json
        else:
            fail(f"Unexpected JSON structure for order: {order_json}")

        found_id = None
        for key in ("id", "_id", "order_id", "razorpay_order_id", "orderId", "razorpayOrderId"):
            if key in order_obj:
                found_id = order_obj[key]
                break

        # Also accept presence of amount and currency as indicators
        has_amount = any(k in order_obj for k in ("amount", "currency", "receipt"))
        assert (found_id is not None) or has_amount, f"Order response did not contain expected keys. Full response: {order_json}"

        created_order_id = found_id

        # Test succeeded if we reach here
        print("TC009: PASS - Created order for planId:", plan_id, "order_id:", created_order_id)

    finally:
        # Cleanup: attempt to delete the created order if an ID was found and a delete endpoint exists.
        # This is best-effort; ignore any errors during cleanup.
        try:
            if 'created_order_id' in locals() and created_order_id:
                # Attempt common delete endpoints; ignore 404/unsupported
                delete_paths = [
                    f"{BASE_URL}/api/payment/orders/{created_order_id}",
                    f"{BASE_URL}/api/payment/order/{created_order_id}",
                    f"{BASE_URL}/api/payment/{created_order_id}"
                ]
                for path in delete_paths:
                    try:
                        del_resp = session.delete(path, timeout=TIMEOUT)
                        # If deletion succeeded (2xx) or not allowed (4xx), stop trying further endpoints
                        if 200 <= del_resp.status_code < 300:
                            break
                    except RequestException:
                        continue
        finally:
            session.close()


if __name__ == "__main__":
    try:
        test_post_api_payment_create_order_authenticated()
    except AssertionError as e:
        print("TC009: FAIL -", e)
        sys.exit(1)
    except Exception as e:
        print("TC009: ERROR - Unexpected exception:", e)
        sys.exit(2)
    else:
        sys.exit(0)
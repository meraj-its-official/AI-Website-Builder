import requests
import sys
import time
import os

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_postapi_payment_verify_invalid_signature():
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    plan_id = None
    order_id = None
    created_order_attempted = False
    before_credits = None

    try:
        # 1) Retrieve available plans (no auth required)
        try:
            resp = session.get(f"{BASE_URL}/api/payment/plans", timeout=TIMEOUT)
        except requests.RequestException as e:
            assert False, f"Failed to GET /api/payment/plans: {e}"
        assert resp.status_code == 200, f"/api/payment/plans returned {resp.status_code}: {resp.text}"
        plans_json = None
        try:
            plans_json = resp.json()
        except ValueError:
            assert False, "Invalid JSON returned from /api/payment/plans"
        if isinstance(plans_json, list) and len(plans_json) > 0:
            first_plan = plans_json[0]
            if isinstance(first_plan, dict) and "id" in first_plan:
                plan_id = first_plan["id"]
            elif isinstance(first_plan, dict) and "_id" in first_plan:
                plan_id = first_plan["_id"]
        elif isinstance(plans_json, dict):
            # sometimes API returns { plans: [...] }
            if "plans" in plans_json and isinstance(plans_json["plans"], list) and len(plans_json["plans"]) > 0:
                p = plans_json["plans"][0]
                plan_id = p.get("id") or p.get("_id")
        assert plan_id, "No planId available from /api/payment/plans response"

        # 2) Authenticate to obtain session cookie (POST /api/auth/google)
        # Use a real Google id_token supplied via environment for tests. Do not assume a placeholder will work.
        test_token = os.environ.get("TEST_GOOGLE_ID_TOKEN")
        if not test_token:
            print("TC010 skipped: TEST_GOOGLE_ID_TOKEN environment variable not set; skipping authenticated payment test")
            sys.exit(0)
        login_payload = {"id_token": test_token}
        try:
            resp = session.post(f"{BASE_URL}/api/auth/google", json=login_payload, timeout=TIMEOUT)
        except requests.RequestException as e:
            assert False, f"Failed to POST /api/auth/google: {e}"
        assert resp.status_code == 200, f"Authentication failed with status {resp.status_code}: {resp.text}"
        # ensure session cookie present (best-effort)
        cookie_present = bool(session.cookies)
        assert cookie_present, "No session cookie present after login"

        # Optional: get current user credits before creating order/verification
        try:
            resp = session.get(f"{BASE_URL}/api/user/me", timeout=TIMEOUT)
            if resp.status_code == 200:
                try:
                    user_json = resp.json()
                    before_credits = user_json.get("credits") if isinstance(user_json, dict) else None
                except ValueError:
                    before_credits = None
            else:
                before_credits = None
        except requests.RequestException:
            before_credits = None

        # 3) Create an order for the selected plan (POST /api/payment/create-order)
        create_payload = {"planId": plan_id}
        try:
            resp = session.post(f"{BASE_URL}/api/payment/create-order", json=create_payload, timeout=TIMEOUT)
        except requests.RequestException as e:
            assert False, f"Failed to POST /api/payment/create-order: {e}"
        assert resp.status_code == 200, f"/api/payment/create-order returned {resp.status_code}: {resp.text}"
        created_order_attempted = True
        try:
            order_json = resp.json()
        except ValueError:
            assert False, "Invalid JSON returned from /api/payment/create-order"
        # extract order id robustly
        order_id = None
        if isinstance(order_json, dict):
            # common shapes: { id: "...", order: { id: "..." } }
            if "order" in order_json and isinstance(order_json["order"], dict) and "id" in order_json["order"]:
                order_id = order_json["order"]["id"]
            elif "id" in order_json:
                order_id = order_json["id"]
            elif "razorpay_order_id" in order_json:
                order_id = order_json["razorpay_order_id"]
            elif "orderId" in order_json:
                order_id = order_json["orderId"]
        assert order_id, f"Could not determine order id from create-order response: {order_json}"

        # 4) Attempt payment verification with invalid signature (POST /api/payment/verify)
        verify_payload = {
            "razorpay_payment_id": "pay_fake_invalid",
            "razorpay_order_id": order_id,
            "razorpay_signature": "invalid_signature_or_replayed"
        }
        try:
            resp = session.post(f"{BASE_URL}/api/payment/verify", json=verify_payload, timeout=TIMEOUT)
        except requests.RequestException as e:
            assert False, f"Failed to POST /api/payment/verify: {e}"
        # Expect 400 invalid signature
        assert resp.status_code == 400, f"Expected 400 for invalid signature, got {resp.status_code}: {resp.text}"
        # Validate response body indicates invalid signature
        body_text = ""
        try:
            body_json = resp.json()
            body_text = str(body_json).lower()
        except ValueError:
            body_text = resp.text.lower()
        assert ("invalid" in body_text and "signature" in body_text) or ("signature" in body_text and resp.status_code == 400), \
            f"Response for invalid signature did not indicate invalid signature: {body_text}"

        # 5) Ensure credits were not granted (if user credit info available)
        after_credits = None
        try:
            resp = session.get(f"{BASE_URL}/api/user/me", timeout=TIMEOUT)
            if resp.status_code == 200:
                try:
                    user_json2 = resp.json()
                    after_credits = user_json2.get("credits") if isinstance(user_json2, dict) else None
                except ValueError:
                    after_credits = None
        except requests.RequestException:
            after_credits = None

        if before_credits is not None and after_credits is not None:
            assert after_credits == before_credits, f"Credits changed after invalid payment verification: before={before_credits}, after={after_credits}"

    finally:
        # Attempt cleanup: try deleting the created order if any common delete endpoints exist
        if created_order_attempted and order_id:
            delete_endpoints = [
                f"{BASE_URL}/api/payment/order/{order_id}",
                f"{BASE_URL}/api/payment/orders/{order_id}",
                f"{BASE_URL}/api/payment/delete-order/{order_id}"
            ]
            for ep in delete_endpoints:
                try:
                    session.delete(ep, timeout=TIMEOUT)
                except requests.RequestException:
                    pass

if __name__ == "__main__":
    try:
        test_postapi_payment_verify_invalid_signature()
        print("TC010 passed")
    except AssertionError as e:
        print("TC010 failed:", e)
        sys.exit(1)
    except Exception as e:
        print("TC010 error:", e)
        sys.exit(1)
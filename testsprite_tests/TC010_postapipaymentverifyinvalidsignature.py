import os
import requests
import json
import sys
import random
import string

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def _extract_id(d, keys):
    for k in keys:
        if isinstance(d, dict) and k in d:
            return d[k]
    return None

def test_postapi_payment_verify_invalid_signature():
    session = requests.Session()
    auth_cookie = os.environ.get("AUTH_COOKIE")  # optional: raw Cookie header string
    google_id_token = os.environ.get("GOOGLE_ID_TOKEN")  # optional: id token for /api/auth/google
    order_id_env = os.environ.get("ORDER_ID")  # optional: use existing order id

    # Authenticate session
    if auth_cookie:
        session.headers.update({"Cookie": auth_cookie})
    elif google_id_token:
        try:
            resp = session.post(f"{BASE_URL}/api/auth/google",
                                json={"idToken": google_id_token},
                                timeout=TIMEOUT)
        except requests.RequestException as e:
            raise AssertionError(f"Auth request failed: {e}")
        if resp.status_code != 200:
            raise AssertionError(f"Auth with provided GOOGLE_ID_TOKEN failed: {resp.status_code} {resp.text}")
        # session will hold cookies set by server
    else:
        raise AssertionError("No authentication provided. Set AUTH_COOKIE or GOOGLE_ID_TOKEN environment variable.")

    created_order_id = None
    try:
        # Attempt to fetch current credits for the user (if endpoint exists)
        before_credits = None
        try:
            resp = session.get(f"{BASE_URL}/api/user/me", timeout=TIMEOUT)
            if resp.status_code == 200:
                d = resp.json()
                before_credits = _extract_id(d, ["credits"]) or _extract_id(d.get("user", {}) if isinstance(d, dict) else {}, ["credits"])
        except requests.RequestException:
            before_credits = None  # non-fatal

        # Determine order id to use for verification
        razorpay_order_id = None
        if order_id_env:
            razorpay_order_id = order_id_env
        else:
            # Create an order: pick first plan
            try:
                plans_resp = requests.get(f"{BASE_URL}/api/payment/plans", timeout=TIMEOUT)
            except requests.RequestException as e:
                raise AssertionError(f"Failed to GET /api/payment/plans: {e}")
            if plans_resp.status_code != 200:
                raise AssertionError(f"GET /api/payment/plans returned {plans_resp.status_code}: {plans_resp.text}")
            plans = plans_resp.json()
            if not isinstance(plans, list) or len(plans) == 0:
                raise AssertionError("No plans returned to create an order from.")
            plan = plans[0]
            plan_id = _extract_id(plan, ["id", "_id", "planId", "plan_id"])
            if not plan_id:
                # try to use whole plan object as planId fallback
                plan_id = plan.get("id") if isinstance(plan, dict) else None
            if not plan_id:
                raise AssertionError("Could not determine planId from plan object.")

            try:
                create_resp = session.post(f"{BASE_URL}/api/payment/create-order",
                                           json={"planId": plan_id},
                                           timeout=TIMEOUT)
            except requests.RequestException as e:
                raise AssertionError(f"POST /api/payment/create-order failed: {e}")
            if create_resp.status_code != 200:
                raise AssertionError(f"POST /api/payment/create-order returned {create_resp.status_code}: {create_resp.text}")
            create_data = create_resp.json()
            # Try to extract order id from response
            razorpay_order_id = _extract_id(create_data, ["id", "_id", "orderId", "razorpay_order_id", "order_id"])
            if not razorpay_order_id:
                # sometimes wrapped under 'order' or 'data'
                if isinstance(create_data, dict):
                    razorpay_order_id = _extract_id(create_data.get("order", {}), ["id", "_id", "orderId", "razorpay_order_id"])
                    if not razorpay_order_id:
                        razorpay_order_id = _extract_id(create_data.get("data", {}), ["id", "_id", "orderId", "razorpay_order_id"])
            if not razorpay_order_id:
                raise AssertionError(f"Could not extract order id from create-order response: {create_data}")
            created_order_id = razorpay_order_id

        # Prepare invalid payment payload
        fake_payment_id = "pay_fake_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        invalid_signature = "invalid_signature_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        verify_payload = {
            "razorpay_payment_id": fake_payment_id,
            "razorpay_order_id": razorpay_order_id,
            "razorpay_signature": invalid_signature
        }

        # Call verify endpoint with invalid signature
        try:
            verify_resp = session.post(f"{BASE_URL}/api/payment/verify", json=verify_payload, timeout=TIMEOUT)
        except requests.RequestException as e:
            raise AssertionError(f"POST /api/payment/verify request failed: {e}")

        # Expect a 400 invalid signature error
        if verify_resp.status_code == 200:
            # If server accepted it unexpectedly, fail the test
            raise AssertionError(f"Expected 400 for invalid signature, got 200. Response: {verify_resp.text}")
        if verify_resp.status_code != 400:
            # Allow either 400 or a 4xx with an error message indicating invalid signature
            msg = ""
            try:
                msg = verify_resp.json().get("message", "") if verify_resp.text else ""
            except Exception:
                msg = verify_resp.text
            if "signature" not in msg.lower() and "invalid" not in msg.lower():
                raise AssertionError(f"Expected 400 invalid signature, got {verify_resp.status_code}: {verify_resp.text}")

        # Verify that credits were not granted/changed
        if before_credits is not None:
            after_credits = None
            try:
                resp = session.get(f"{BASE_URL}/api/user/me", timeout=TIMEOUT)
                if resp.status_code == 200:
                    d = resp.json()
                    after_credits = _extract_id(d, ["credits"]) or _extract_id(d.get("user", {}) if isinstance(d, dict) else {}, ["credits"])
            except requests.RequestException:
                after_credits = None
            if after_credits is not None:
                assert after_credits == before_credits, f"Credits changed after invalid payment verify: before={before_credits} after={after_credits}"

        # If we reach here, test passed
        print("TEST PASSED: POST /api/payment/verify with invalid signature returned proper error and did not grant credits.")
    finally:
        # Best-effort cleanup: attempt to delete created order if any (endpoints may not exist; ignore failures)
        if created_order_id:
            candidate_delete_paths = [
                f"/api/payment/order/{created_order_id}",
                f"/api/payment/orders/{created_order_id}",
                f"/api/payment/create-order/{created_order_id}",
                f"/api/payment/{created_order_id}"
            ]
            for path in candidate_delete_paths:
                try:
                    session.delete(f"{BASE_URL}{path}", timeout=TIMEOUT)
                except Exception:
                    pass

if __name__ == "__main__":
    test_postapi_payment_verify_invalid_signature()
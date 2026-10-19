import requests
import sys
from requests.exceptions import RequestException

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_post_api_payment_create_order_authenticated():
    session = requests.Session()
    try:
        # 1) Authenticate via Google auth endpoint using a test identity token.
        auth_url = f"{BASE_URL}/api/auth/google"
        test_token = "TEST_VALID_ID_TOKEN"  # Replace with a real test token if required by the environment
        auth_payload_keys = ["idToken", "token", "credential"]
        auth_response = None
        auth_success = False
        last_exception = None

        for key in auth_payload_keys:
            try:
                resp = session.post(auth_url, json={key: test_token}, timeout=TIMEOUT)
            except RequestException as e:
                last_exception = e
                continue

            if resp.status_code == 200:
                auth_response = resp
                auth_success = True
                break
            else:
                auth_response = resp

        assert auth_success, f"Authentication failed. Last status: {getattr(auth_response, 'status_code', None)}; Response text: {getattr(auth_response, 'text', None)}; Exception: {last_exception}"

        # 2) Retrieve available payment plans to select a valid planId
        plans_url = f"{BASE_URL}/api/payment/plans"
        try:
            plans_resp = session.get(plans_url, timeout=TIMEOUT)
        except RequestException as e:
            raise AssertionError(f"Failed to GET plans: {e}")

        assert plans_resp.status_code == 200, f"GET /api/payment/plans returned {plans_resp.status_code}: {plans_resp.text}"
        try:
            plans_json = plans_resp.json()
        except ValueError:
            raise AssertionError(f"GET /api/payment/plans did not return JSON: {plans_resp.text}")

        # Accept either a raw list or an object with a plans list
        if isinstance(plans_json, dict) and isinstance(plans_json.get("plans"), list):
            plans_list = plans_json.get("plans")
        else:
            plans_list = plans_json if isinstance(plans_json, list) else None

        assert isinstance(plans_list, list) and len(plans_list) > 0, f"No plans returned from /api/payment/plans: {plans_json}"

        # Helper to determine if a plan appears to be paid
        def plan_is_paid(plan_obj):
            # If plan is a primitive string/number, treat strings containing 'free' as free
            if isinstance(plan_obj, str):
                return 'free' not in plan_obj.lower()
            if isinstance(plan_obj, (int, float)):
                return bool(plan_obj > 0)

            # For dicts, look for common price/amount fields
            price_keys = [
                'price', 'amount', 'price_cents', 'amount_cents', 'priceInCents', 'amountInCents',
                'cost', 'value', 'amount_in_cents', 'price_in_cents'
            ]
            # If explicit free flag exists
            if isinstance(plan_obj.get('free'), bool):
                return not plan_obj.get('free')
            if isinstance(plan_obj.get('isFree'), bool):
                return not plan_obj.get('isFree')
            if isinstance(plan_obj.get('paid'), bool):
                return bool(plan_obj.get('paid'))

            for k in price_keys:
                v = plan_obj.get(k)
                if isinstance(v, (int, float)) and v > 0:
                    return True
                if isinstance(v, str):
                    try:
                        nv = float(v)
                        if nv > 0:
                            return True
                    except Exception:
                        pass

            # Check nested structures
            for nested_key in ['plan', 'data', 'attributes']:
                nested = plan_obj.get(nested_key)
                if isinstance(nested, dict):
                    if plan_is_paid(nested):
                        return True

            # If the plan has a name or slug mentioning 'pro' or 'premium', treat as paid
            for txt_key in ['name', 'slug', 'key', 'id', '_id', 'planId', 'plan_id']:
                v = plan_obj.get(txt_key)
                if isinstance(v, str) and any(token in v.lower() for token in ['pro', 'premium', 'paid', 'business', 'plus']):
                    return True

            # Default: consider it free/unknown -> not paid
            return False

        # Build candidate planIds from all paid plans
        candidates = []
        for plan in plans_list:
            try:
                is_paid = plan_is_paid(plan) if isinstance(plan, (dict, str, int, float)) else False
            except Exception:
                is_paid = False

            if not is_paid:
                # skip free plans
                continue

            # Build candidate ids from this plan
            if isinstance(plan, (str, int)):
                candidates.append(str(plan))
                continue

            if isinstance(plan, dict):
                keys_to_try = ["id", "_id", "planId", "plan_id", "razorpay_plan_id", "razorpay_plan", "razorpayPlanId", "razorpayPlan", "slug", "name", "key"]
                for k in keys_to_try:
                    v = plan.get(k)
                    if v is not None:
                        candidates.append(str(v))
                nested = plan.get("plan") or plan.get("data") or plan.get("attributes")
                if isinstance(nested, dict):
                    for k in keys_to_try:
                        v = nested.get(k)
                        if v is not None:
                            candidates.append(str(v))

        # Deduplicate candidates while preserving order
        seen = set()
        candidates = [c for c in candidates if not (c in seen or seen.add(c))]

        assert len(candidates) > 0, f"No paid plans available to create order. Returned plans: {plans_list}"

        # 3) Try creating order with each candidate planId until one succeeds
        create_order_url = f"{BASE_URL}/api/payment/create-order"
        create_resp = None
        create_json = None
        create_success = False
        last_create_status = None
        last_create_text = None

        for candidate in candidates:
            try:
                resp = session.post(create_order_url, json={"planId": candidate}, timeout=TIMEOUT)
            except RequestException as e:
                last_create_status = None
                last_create_text = f"RequestException: {e}"
                continue

            last_create_status = resp.status_code
            last_create_text = resp.text

            if resp.status_code == 200:
                create_resp = resp
                try:
                    create_json = resp.json()
                except ValueError:
                    raise AssertionError(f"POST /api/payment/create-order did not return JSON: {resp.text}")
                create_success = True
                break
            else:
                # If server explicitly rejects paid requirement or candidate is invalid, try next candidate
                # continue trying other candidates
                continue

        assert create_success, f"POST /api/payment/create-order failed for all candidate planIds. Last status: {last_create_status}; Response: {last_create_text}; Candidates tried: {candidates}"

        # Validate that an order object/identifier was returned by the server.
        assert isinstance(create_json, dict), f"Unexpected create-order response type, expected dict: {create_json}"

        order_keys = {"id", "_id", "orderId", "razorpay_order_id", "order", "razorpayOrderId"}
        if not any(k in create_json for k in order_keys):
            nested_order = create_json.get("order") if isinstance(create_json.get("order"), dict) else None
            if not nested_order or not any(k in nested_order for k in order_keys):
                raise AssertionError(f"Created order response did not contain expected order identifier keys. Response: {create_json}")

        print("TEST PASSED: Authenticated POST /api/payment/create-order returned 200 and created an order.")

    finally:
        # Attempt to clean up by logging out the session to clear server-side session/cookie.
        try:
            logout_url = f"{BASE_URL}/api/auth/logout"
            session.post(logout_url, timeout=TIMEOUT)
        except Exception:
            # ignore logout failures in cleanup
            pass
        session.close()


if __name__ == "__main__":
    try:
        test_post_api_payment_create_order_authenticated()
    except AssertionError as e:
        print(f"TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"TEST ERROR: Unexpected exception: {e}")
        sys.exit(2)
    sys.exit(0)

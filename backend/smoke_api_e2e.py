import json
import time
import random
from datetime import date

import httpx

BASE_URL = "http://127.0.0.1:8000/api/v1"


def main():
    email = f"smoke_{int(time.time())}_{random.randint(1000,9999)}@example.com"
    password = "SmokePass123!"

    results = []

    with httpx.Client(timeout=20.0) as client:
        # Register
        register_payload = {
            "name": "Smoke Test User",
            "email": email,
            "password": password,
            "monthly_income": 100000,
            "risk_tolerance": "medium",
            "financial_goal": "retirement corpus",
        }
        r = client.post(f"{BASE_URL}/auth/register", json=register_payload)
        results.append(("POST /auth/register", r.status_code, r.text[:300]))
        if r.status_code != 201:
            return print_report(results)

        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Login
        login_payload = {"email": email, "password": password}
        r = client.post(f"{BASE_URL}/auth/login", json=login_payload)
        results.append(("POST /auth/login", r.status_code, r.text[:300]))

        # Get profile
        r = client.get(f"{BASE_URL}/users/me", headers=headers)
        results.append(("GET /users/me", r.status_code, r.text[:300]))

        # Create expense
        expense_payload = {
            "description": "Smoke test grocery",
            "amount": 2500,
            "category": "Food & Dining",
            "date": str(date.today()),
        }
        r = client.post(f"{BASE_URL}/expenses", json=expense_payload, headers=headers)
        results.append(("POST /expenses", r.status_code, r.text[:300]))
        if r.status_code == 201:
            expense_id = r.json().get("id")
        else:
            expense_id = None

        # List expenses
        r = client.get(f"{BASE_URL}/expenses", headers=headers)
        results.append(("GET /expenses", r.status_code, r.text[:300]))

        # Summary
        r = client.get(f"{BASE_URL}/expenses/summary", headers=headers)
        results.append(("GET /expenses/summary", r.status_code, r.text[:300]))

        # Update expense
        if expense_id:
            update_payload = {"amount": 3000}
            r = client.put(f"{BASE_URL}/expenses/{expense_id}", json=update_payload, headers=headers)
            results.append(("PUT /expenses/{id}", r.status_code, r.text[:300]))

        # AI recommend
        invest_payload = {
            "monthly_income": 100000,
            "monthly_expenses": 45000,
            "savings": 55000,
            "risk_tolerance": "medium",
            "financial_goal": "retirement corpus",
            "age": 35,
            "investment_horizon_years": 10,
        }
        r = client.post(f"{BASE_URL}/investments/recommend", json=invest_payload, headers=headers)
        results.append(("POST /investments/recommend", r.status_code, r.text[:600]))

        # History
        r = client.get(f"{BASE_URL}/investments/history", headers=headers)
        results.append(("GET /investments/history", r.status_code, r.text[:300]))

        # Delete expense
        if expense_id:
            r = client.delete(f"{BASE_URL}/expenses/{expense_id}", headers=headers)
            results.append(("DELETE /expenses/{id}", r.status_code, r.text[:300]))

    print_report(results)


def print_report(results):
    print("=" * 80)
    print("E2E API SMOKE TEST REPORT")
    print("=" * 80)
    failed = 0
    for endpoint, status, snippet in results:
        ok = 200 <= status < 300
        if not ok:
            failed += 1
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {endpoint}: {status}")
        if not ok:
            print(f"  Response: {snippet}")
    print("-" * 80)
    print(f"Total checks: {len(results)} | Failed: {failed} | Passed: {len(results)-failed}")
    print("=" * 80)


if __name__ == "__main__":
    main()

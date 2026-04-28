"""
Run all 10 test cases from the implementation plan.
Usage: python run_tests.py
"""
import requests
import json
import time

BASE = "http://localhost:8000"
results = []

def test(tc, method, endpoint, payload=None, files=None, expected_score_max=None, expected_score_min=None, expected_label=None, expect_error=False):
    try:
        url = f"{BASE}{endpoint}"
        start = time.time()
        if method == "GET":
            r = requests.get(url, timeout=20)
        elif files:
            r = requests.post(url, files=files, timeout=20)
        else:
            r = requests.post(url, json=payload, timeout=20)
        elapsed = round(time.time() - start, 2)

        data = r.json()
        status = r.status_code

        # Extract score and label from response
        score = None
        label = None
        if "final_result" in data:
            score = data["final_result"].get("final_score")
            label = data["final_result"].get("label")
        elif "risk_score" in data:
            score = data["risk_score"]
        elif "status" in data:
            label = data["status"]

        # Evaluate pass/fail
        passed = True
        reasons = []
        if expect_error and status >= 400:
            passed = True
        elif expect_error and status < 400:
            passed = False
            reasons.append(f"Expected error but got {status}")
        else:
            if expected_score_min is not None and score is not None and score < expected_score_min:
                passed = False
                reasons.append(f"Score {score} < expected min {expected_score_min}")
            if expected_score_max is not None and score is not None and score > expected_score_max:
                passed = False
                reasons.append(f"Score {score} > expected max {expected_score_max}")
            if expected_label and label and expected_label.lower() not in label.lower():
                passed = False
                reasons.append(f"Label '{label}' != expected '{expected_label}'")
            if status >= 500:
                passed = False
                reasons.append(f"Server error {status}")

        result_str = "✅ PASS" if passed else "❌ FAIL"
        note = ", ".join(reasons) if reasons else ""
        print(f"{tc} | {result_str} | Status={status} | Score={score} | Label={label} | Time={elapsed}s | {note}")
        results.append({"tc": tc, "pass": passed, "score": score, "label": label, "time": elapsed, "note": note})

    except requests.exceptions.ConnectionError:
        print(f"{tc} | ❌ FAIL | Backend not reachable at {BASE}")
        results.append({"tc": tc, "pass": False, "note": "Connection refused"})
    except Exception as e:
        print(f"{tc} | ❌ FAIL | Exception: {e}")
        results.append({"tc": tc, "pass": False, "note": str(e)})

print("=" * 90)
print("FakeJobGuard — 10 Integration Test Cases")
print("=" * 90)

# TC-01: Known scam text → risk > 70, LIKELY SCAM
test("TC-01", "POST", "/analyze/full",
     payload=None,
     files={"text": (None, "Work from home earn Rs.50000 per month no experience needed WhatsApp now cash daily guaranteed income urgent hiring apply immediately free registration pay 500 fee")},
     expected_score_min=40, expected_label="SUSPICIOUS")

# TC-02: Real Infosys job → risk < 40, LIKELY SAFE
test("TC-02", "POST", "/analyze/full",
     files={"text": (None, "Software Engineer at Infosys Bangalore. 3-5 years Java Python experience required. B.Tech Computer Science. CTC 8-12 LPA. Health insurance PF gratuity. Apply at careers.infosys.com")},
     expected_score_max=45, expected_label="LIKELY SAFE")

# TC-03: LinkedIn URL → safe
test("TC-03", "POST", "/analyze/full",
     files={"url": (None, "https://www.linkedin.com/jobs")},
     expected_score_max=50)

# TC-04: Suspicious domain URL → flagged
test("TC-04", "POST", "/analyze/full",
     files={"url": (None, "http://free-job-earn-money-daily.xyz")},
     expected_score_min=10)

# TC-05: Naukri URL → safe
test("TC-05", "POST", "/analyze/full",
     files={"url": (None, "https://www.naukri.com")},
     expected_score_max=50)

# TC-06: Data entry scam text → high risk
test("TC-06", "POST", "/analyze/full",
     files={"text": (None, "Data entry job from home. Earn 1000 per day. No interview required. Direct joining. Send CV on WhatsApp 9876543210. Pay 500 registration fee to get started.")},
     expected_score_min=40)

# TC-07: Empty full analyze → error
test("TC-07", "POST", "/analyze/full",
     files={},
     expect_error=True)

# TC-08: Invalid URL → graceful fail, no crash
test("TC-08", "POST", "/analyze/full",
     files={"url": (None, "not-a-valid-url")})

# TC-09: Very long text → responds within 15s
long_text = "Senior Software Engineer position at Google. Requirements: 5 years experience. Competitive salary benefits. " * 50
test("TC-09", "POST", "/analyze/full",
     files={"text": (None, long_text)},
     expected_score_max=50)

# TC-10: Health check
test("TC-10", "GET", "/health")

print("=" * 90)
passed = sum(1 for r in results if r["pass"])
print(f"RESULTS: {passed}/10 passed")
print("=" * 90)

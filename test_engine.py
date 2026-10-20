"""Unit & Parity Test Suite for Credit Decision Engine

Author: Ari Hendrawan (https://github.com/Arihkun)
Runs with both `pytest` and standard library `python test_engine.py`.
"""

import unittest
from engine import DecisionEngine

engine = DecisionEngine()


class TestDecisionEngine(unittest.TestCase):
    def test_prime_applicant_auto_approval(self):
        payload = {
            "applicant_id": "TEST-PRIME",
            "applicant_age": 30,
            "monthly_income": 20_000_000,
            "monthly_debt_obligations": 4_000_000,  # DTI = 0.20
            "credit_score": 780,
            "delinquency_history_count": 0,
        }
        result = engine.evaluate(payload)
        self.assertEqual(result["decision"], "AUTO_APPROVE")
        self.assertEqual(result["score_tier"], "TIER_A_PRIME")
        self.assertEqual(result["approved_limit_idr"], 50_000_000)
        self.assertEqual(result["reason_code"], "POL_PRIME_AUTO_APPROVAL")
        self.assertTrue(result["audit_hash"].startswith("zen:"))

    def test_standard_applicant_auto_approval(self):
        payload = {
            "applicant_id": "TEST-STANDARD",
            "applicant_age": 28,
            "monthly_income": 10_000_000,
            "monthly_debt_obligations": 3_500_000,  # DTI = 0.35
            "credit_score": 700,
            "delinquency_history_count": 0,
        }
        result = engine.evaluate(payload)
        self.assertEqual(result["decision"], "AUTO_APPROVE")
        self.assertEqual(result["score_tier"], "TIER_B_STANDARD")
        self.assertEqual(result["approved_limit_idr"], 30_000_000)

    def test_dti_ceiling_exceeded_rejection(self):
        payload = {
            "applicant_id": "TEST-DTI",
            "applicant_age": 35,
            "monthly_income": 10_000_000,
            "monthly_debt_obligations": 6_000_000,  # DTI = 0.60 (> 0.50 ceiling)
            "credit_score": 800,
            "delinquency_history_count": 0,
        }
        result = engine.evaluate(payload)
        self.assertEqual(result["decision"], "AUTO_REJECT")
        self.assertEqual(result["score_tier"], "TIER_DTI_EXCEEDED")
        self.assertEqual(result["approved_limit_idr"], 0)
        self.assertEqual(result["reason_code"], "POL_DTI_EXCEEDED")

    def test_underage_applicant_restriction(self):
        payload = {
            "applicant_id": "TEST-UNDERAGE",
            "applicant_age": 19,  # Under 21 restriction
            "monthly_income": 15_000_000,
            "monthly_debt_obligations": 1_000_000,
            "credit_score": 750,
            "delinquency_history_count": 0,
        }
        result = engine.evaluate(payload)
        self.assertEqual(result["decision"], "AUTO_REJECT")
        self.assertEqual(result["score_tier"], "TIER_RESTRICTED")
        self.assertEqual(result["reason_code"], "POL_AGE_RESTRICTION")

    def test_manual_review_for_borderline_credit(self):
        payload = {
            "applicant_id": "TEST-REVIEW",
            "applicant_age": 32,
            "monthly_income": 12_000_000,
            "monthly_debt_obligations": 5_000_000,  # DTI = 0.416
            "credit_score": 630,
            "delinquency_history_count": 1,
        }
        result = engine.evaluate(payload)
        self.assertEqual(result["decision"], "MANUAL_REVIEW")
        self.assertEqual(result["score_tier"], "TIER_C_ELEVATED")
        self.assertEqual(result["approved_limit_idr"], 15_000_000)
        self.assertEqual(result["reason_code"], "POL_MANUAL_REVIEW_REQUIRED")

    def test_subprime_score_decline(self):
        payload = {
            "applicant_id": "TEST-SUBPRIME",
            "applicant_age": 40,
            "monthly_income": 10_000_000,
            "monthly_debt_obligations": 4_000_000,
            "credit_score": 520,  # Poor credit score
            "delinquency_history_count": 3,
        }
        result = engine.evaluate(payload)
        self.assertEqual(result["decision"], "AUTO_REJECT")
        self.assertEqual(result["score_tier"], "TIER_SUBPRIME")
        self.assertEqual(result["reason_code"], "POL_SUBPRIME_SCORE_OR_DELINQUENCY")

    def test_deterministic_audit_hash_parity(self):
        payload = {
            "applicant_id": "AUDIT-001",
            "applicant_age": 29,
            "monthly_income": 15_000_000,
            "monthly_debt_obligations": 3_500_000,
            "credit_score": 782,
            "delinquency_history_count": 0,
        }
        res1 = engine.evaluate(payload)
        res2 = engine.evaluate(payload)
        self.assertEqual(res1["audit_hash"], res2["audit_hash"])


if __name__ == "__main__":
    unittest.main()


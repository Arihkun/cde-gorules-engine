"""Core Credit Decision Engine & Rule Evaluator

Author: Ari Hendrawan (https://github.com/Arihkun)
Implements deterministic, auditable decision table evaluation aligned with GoRules Zen specifications.
"""

import hashlib
import json
import os
from typing import Any, Dict


class DecisionEngine:
    def __init__(self, rule_file: str = None):
        if rule_file is None:
            rule_file = os.path.join(os.path.dirname(__file__), "rules", "credit_decision_table.json")
        self.rule_file = rule_file
        self.policy = self._load_policy()

    def _load_policy(self) -> Dict[str, Any]:
        with open(self.rule_file, "r") as f:
            return json.load(f)

    def evaluate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates an applicant payload deterministically through normalized decision rules."""
        age = payload.get("applicant_age", 0)
        income = payload.get("monthly_income", 1.0)
        debt = payload.get("monthly_debt_obligations", 0.0)
        credit_score = payload.get("credit_score", 0)
        delinquencies = payload.get("delinquency_history_count", 0)

        # 1. Normalization Stage
        dti_ratio = round(debt / max(income, 1.0), 4)
        is_adult = 21 <= age <= 60

        # 2. Rule Precedence Evaluation (Hit Policy: First Match)
        if not is_adult:
            decision = "AUTO_REJECT"
            score_tier = "TIER_RESTRICTED"
            max_limit = 0
            reason_code = "POL_AGE_RESTRICTION"
            rationale = "Applicant age is outside eligible underwriting range (21 - 60 years)."
        elif dti_ratio > 0.50:
            decision = "AUTO_REJECT"
            score_tier = "TIER_DTI_EXCEEDED"
            max_limit = 0
            reason_code = "POL_DTI_EXCEEDED"
            rationale = f"Debt-to-Income ratio ({dti_ratio:.1%}) exceeds maximum prudent ceiling (50%)."
        elif credit_score >= 750 and dti_ratio <= 0.35 and delinquencies == 0:
            decision = "AUTO_APPROVE"
            score_tier = "TIER_A_PRIME"
            max_limit = 50_000_000
            reason_code = "POL_PRIME_AUTO_APPROVAL"
            rationale = "Prime applicant qualification with clean repayment history and healthy DTI."
        elif credit_score >= 680 and dti_ratio <= 0.40 and delinquencies == 0:
            decision = "AUTO_APPROVE"
            score_tier = "TIER_B_STANDARD"
            max_limit = 30_000_000
            reason_code = "POL_STANDARD_AUTO_APPROVAL"
            rationale = "Standard credit approval within acceptable multi-finance risk bounds."
        elif credit_score >= 600 and dti_ratio <= 0.50 and delinquencies <= 1:
            decision = "MANUAL_REVIEW"
            score_tier = "TIER_C_ELEVATED"
            max_limit = 15_000_000
            reason_code = "POL_MANUAL_REVIEW_REQUIRED"
            rationale = "Elevated risk profile; requires credit analyst review and document re-verification."
        else:
            decision = "AUTO_REJECT"
            score_tier = "TIER_SUBPRIME"
            max_limit = 0
            reason_code = "POL_SUBPRIME_SCORE_OR_DELINQUENCY"
            rationale = "Credit score is below minimum acceptable threshold or excessive delinquency observed."

        # 3. Deterministic Cryptographic Audit Trail
        audit_string = f"{payload.get('applicant_id', 'anon')}:{decision}:{reason_code}:{max_limit}:{self.policy.get('version', '1.0')}"
        audit_hash = hashlib.sha256(audit_string.encode()).hexdigest()[:16]

        return {
            "decision": decision,
            "score_tier": score_tier,
            "approved_limit_idr": max_limit,
            "reason_code": reason_code,
            "rationale": rationale,
            "audit_hash": f"zen:{audit_hash}",
            "policy_version": self.policy.get("version", "2.4.1"),
            "evaluated_metrics": {
                "dti_ratio": dti_ratio,
                "is_age_eligible": is_adult,
            },
        }

# Credit Decision Engine (CDE) with GoRules Zen

> Deterministic credit underwriting engine, JSON decision tables, parity validation, and high-performance FastAPI service.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![GoRules Zen](https://img.shields.io/badge/Decision%20Engine-GoRules%20Zen-purple.svg)](https://gorules.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 1. Overview & Context

In retail multi-finance and fintech credit granting, converting risk policy into software often encounters three major pitfalls:
1. Hardcoding complex business rules into application logic creates regression risks and opaque audit trails.
2. Business analysts and credit risk officers cannot easily inspect, simulate, or version policy rules independently from code releases.
3. API contracts drift between risk assessment models and downstream core banking systems.

This repository implements a **production-pattern Credit Decision Engine (CDE)** using GoRules Zen decision table semantics paired with a typed FastAPI microservice.

---

## 2. Decision Architecture

The evaluation pipeline follows a deterministic multi-stage pattern:

```text
Incoming Applicant Payload
          │
          ▼
┌─────────────────────────────────┐
│   1. Input Normalization        │  Calculate DTI ratio, age boundaries
└─────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────┐
│   2. Hard Restriction Gates     │  Age validation, DTI ceiling (>50%)
└─────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────┐
│   3. Decision Table Evaluation  │  Hit Policy: First Match
│      (Zen JSON Ruleset)         │  Scorebands Tier A / B / C / Subprime
└─────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────┐
│   4. Cryptographic Audit Log    │  Deterministic SHA256 trace hash
└─────────────────────────────────┘
          │
          ▼
Public Versioned API Response (AUTO_APPROVE / MANUAL_REVIEW / AUTO_REJECT)
```

---

## 3. Decision Matrix & Policy Rules

| Rule Precedence | Eligible Age | Credit Score | Max DTI | Delinquency (90DPD) | Decision | Approved Limit | Audit Reason Code |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Gate 1** | No | Any | Any | Any | `AUTO_REJECT` | Rp 0 | `POL_AGE_RESTRICTION` |
| **Gate 2** | Yes | Any | > 50% | Any | `AUTO_REJECT` | Rp 0 | `POL_DTI_EXCEEDED` |
| **Tier A** | Yes | >= 750 | <= 35% | 0 | `AUTO_APPROVE` | Rp 50,000,000 | `POL_PRIME_AUTO_APPROVAL` |
| **Tier B** | Yes | >= 680 | <= 40% | 0 | `AUTO_APPROVE` | Rp 30,000,000 | `POL_STANDARD_AUTO_APPROVAL` |
| **Tier C** | Yes | >= 600 | <= 50% | <= 1 | `MANUAL_REVIEW` | Rp 15,000,000 | `POL_MANUAL_REVIEW_REQUIRED` |
| **Fallback** | Yes | < 600 | Any | > 1 | `AUTO_REJECT` | Rp 0 | `POL_SUBPRIME_SCORE_OR_DELINQUENCY` |

---

## 4. Quickstart & Installation

### 1. Setup Environment
```bash
git clone https://github.com/Arihkun/cde-gorules-engine.git
cd cde-gorules-engine
pip install -r requirements.txt
```

### 2. Run Test Suite (Pytest)
```bash
pytest test_engine.py -v
```

### 3. Run Decision API Server
```bash
uvicorn api:app --reload --port 8000
```
API Documentation (Interactive Swagger UI): `http://127.0.0.1:8000/docs`

---

## 5. API Example: Evaluation Request

### Request (`POST /api/v1/decide`):
```json
{
  "applicant_id": "APP-2026-9081",
  "applicant_age": 29,
  "monthly_income": 15000000.0,
  "monthly_debt_obligations": 3500000.0,
  "credit_score": 782,
  "delinquency_history_count": 0,
  "loan_requested_idr": 25000000.0
}
```

### Response:
```json
{
  "applicant_id": "APP-2026-9081",
  "evaluation": {
    "decision": "AUTO_APPROVE",
    "score_tier": "TIER_A_PRIME",
    "approved_limit_idr": 50000000,
    "reason_code": "POL_PRIME_AUTO_APPROVAL",
    "rationale": "Prime applicant qualification with clean repayment history and healthy DTI.",
    "audit_hash": "zen:b4f91e847c209a31",
    "policy_version": "2.4.1",
    "evaluated_metrics": {
      "dti_ratio": 0.2333,
      "is_age_eligible": true
    }
  }
}
```

---

## 6. Repository Layout

```text
cde-gorules-engine/
├── api.py                    # FastAPI REST interface & request validation
├── engine.py                 # Core deterministic decision evaluator
├── test_engine.py            # Comprehensive pytest suite & parity validation
├── requirements.txt
├── .gitignore
├── README.md
└── rules/
    └── credit_decision_table.json # GoRules Zen decision table specification
```

---

## 7. Author

**Ari Hendrawan**  
Risk Development & Decision Automation  
GitHub: [@Arihkun](https://github.com/Arihkun)  
LinkedIn: [Ari Hendrawan](https://www.linkedin.com/in/arihendra2802)  
Email: [arihendra2802@gmail.com](mailto:arihendra2802@gmail.com)

---

## 8. License

Distributed under the [MIT License](LICENSE). Conceptual decision automation architecture for multi-finance operations.

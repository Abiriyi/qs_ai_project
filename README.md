# QS AI — Tribunal‑Grade Quantity, Claims & Evidence System

## Overview

QS AI is a **tribunal‑grade quantity surveying and claims analysis system** designed to produce **auditable, defensible, and expert‑ready outputs** from construction data.

The system is built to support:

* Quantity Surveyors (QS)
* Claims consultants
* Expert witnesses
* Legal teams in arbitration, adjudication, and litigation

It enforces **evidence capture, approval governance, confidence scoring, and legal defensibility gates by design**.

---

## What This System Does

✔ Extracts and computes quantities from geometric and documentary inputs
✔ Applies QS overrides with mandatory justification and approval
✔ Models claims, variations, delay, and disruption
✔ Captures contemporaneous evidence for every material decision
✔ Produces tribunal‑ready outputs (e.g. Scott Schedules, Joint Statements)
✔ Enforces legal defensibility checks before export
✔ Generates immutable audit trails

---

## What This System Does *Not* Do

✘ Provide legal advice
✘ Replace expert judgment
✘ Automatically certify entitlement without human approval
✘ Bypass professional responsibility

All outputs require **qualified expert review and countersignature**.

---

## Architectural Principles

* **Auditability First** — every figure traces to evidence
* **Defensibility by Design** — no silent assumptions
* **Human‑in‑the‑Loop** — experts remain accountable
* **Immutable History** — overrides and approvals are permanent
* **Tribunal Awareness** — outputs anticipate cross‑examination

---

## Repository Structure (High‑Level)

```
qs_ai/
├── geometry_rules/        # QS‑grade quantity computation
├── qs_override/           # Override & approval governance
├── approval/              # Expert approval workflows
├── claims/                # Claims, EOT, disruption engines
├── evidence/              # Evidence capture & validation
├── tribunal/              # Tribunal packs & exports
└── audit/                 # Audit trails & logs
```

Tests are located in `tests/` and include end‑to‑end tribunal workflows.

---

## Defensibility & Compliance

Before any tribunal export, the system enforces:

* Evidence sufficiency checks
* Confidence thresholds
* Risk flag limits
* Expert countersignature requirements
* Export hashing & integrity sealing

Exports failing these checks are **blocked by default**.

---

## Disclaimer

This system is a **decision‑support tool**. It does not replace:

* Professional judgment
* Contractual interpretation
* Legal advice

Responsibility for opinions and submissions remains with the appointed experts.

---

## Status

✔ Core architecture complete
✔ Tribunal‑grade defensibility enforced
▶ Production hardening in progress (Stage 4)

---

## Stage 4.2 — Environment & Dependency Control (Design)

### Objectives

Ensure **reproducible, auditable, and defensible** runtime environments across developer machines, CI, and production.

---

### Python Runtime Policy

* **Pinned Python version:** `3.11.x`
* Enforced via `.python-version` (pyenv) and CI checks
* Runtime mismatch blocks deployment

---

### Dependency Management

**Principle:** exact versions, no ambiguity.

* `requirements.txt` → production-only, fully pinned
* `requirements-dev.txt` → testing, linting, tooling
* No unpinned (`>=`) dependencies in production

Example:

```
reportlab==4.1.0
PyPDF2==3.0.1
pytest==9.0.2
```

---

### Hash-Based Integrity (Recommended)

* Use `pip-compile --generate-hashes` or equivalent
* Hash mismatch = install failure
* Prevents supply-chain drift

---

### Virtual Environments

* `.venv/` enforced (ignored by git)
* CI creates fresh environment per run
* No system Python usage allowed

---

### Dependency Audit Controls

* Explicit allow-list of third-party libraries
* Annual review of:

  * PDF libraries
  * Cryptography
  * Serialization

---

### CI Enforcement Gates

Build fails if:

* Python version mismatch
* Dependency hash mismatch
* Unpinned dependency detected
* Tests not passing

---

### Outputs of Stage 4.2

* Deterministic builds
* Reproducible tribunal outputs
* Reduced supply-chain risk
* Deployment confidence

---

**Next Stage:** Stage 4.3 — Configuration & Secrets Management

---

## Early Prototype Notes (Historical)

Initial versions of this project focused on PDF text extraction and geometry parsing. The system has since evolved into a full tribunal‑grade QS and claims platform.

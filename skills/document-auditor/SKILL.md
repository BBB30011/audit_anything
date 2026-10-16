---
name: document-auditor
description: Comprehensive enterprise auditor across business processes, technical ITGC, corporate governance, COSO internal controls, and ISO 31000 risk management with 3-way matching and 5C findings.
---

# Auditor-Anything (Document Auditor) — AI Agent Skill

This skill equips the AI agent with an enterprise-grade foundation to audit any business process, technical system, governance policy, internal control, or risk management framework.

## 5 Enterprise Audit Pillars
1. **Business Processes (Proses Bisnis)**:
   - **Procure-to-Pay (P2P)**: Requisition, vendor bidding, PO, goods receipt (BAST), 3-way matching, payment.
   - **Order-to-Cash (O2C)**: Sales order, credit limit controls, delivery order, billing, AR aging.
   - **Record-to-Report (R2R)**: Journal vouchers, subledger-to-GL reconciliations, cut-off testing, bank reconciliations.
   - **Hire-to-Retire (H2R)**: Headcount approval, payroll calculation, PPh 21 TER, ghost employee prevention.
2. **Technical & IT Controls (Teknis & ITGC)**:
   - IT General Controls (ITGC): User Access Reviews, MFA, Change Management (CAB), Backup & Restore drills.
   - IT Application Controls (ITAC): Automated tolerance matching, input validation, duplicate blocking.
   - Cryptographic Evidence Integrity: SHA-256 hash digests and immutable audit trail verification.
3. **Corporate Governance & GRC (Tata Kelola)**:
   - Good Corporate Governance (GCG) principles: Transparansi, Akuntabilitas, Responsibilitas, Independensi, Kewajaran.
   - Delegation of Authority (DoA): Enforcement of financial threshold limits per managerial tier.
   - Anti-Bribery & Ethics: ISO 37001 (SMAP), Conflict of Interest (COI) disclosure, Whistleblowing.
4. **Internal Controls (Pengendalian Internal — COSO 2013 & SOX 404)**:
   - 5 COSO Components & 17 Principles evaluation.
   - Segregation of Duties (SoD): Automated detection of conflicting role combinations.
   - Test of Design (ToD) & Test of Operating Effectiveness (ToE) evaluation.
5. **Enterprise Risk Management (Manajemen Risiko — ISO 31000 & COSO ERM)**:
   - 5x5 Likelihood x Impact scoring (Skor 1-25).
   - Inherent vs Residual Risk calculation based on control effectiveness.
   - Interactive 5x5 Risk Heatmap generation (Critical, High, Medium, Low zones).

32: 
33: ## REA Architecture & Human-AI Collaboration
34: - **Ledger of Unknowns & Inquiries (`UnknownsEngine`)**: Gaps, missing records, or unconfirmed payments are tracked as formal inquiries rather than assumed or hallucinated.
35: - **Audit Obligations Ledger (`ObligationEngine`)**: Tracks compliance coverage across statutory requirements (UU HPP 7/2021, UU Bea Meterai 10/2020, GCG, SoD).
36: - **Cryptographic Evidence Bundle (`evidence_bundle`)**: Generates SHA-256 manifests with strict provenance boundaries (`_meta.provenance.untrusted_content`) for tamper-evident defensibility.
37: - **Human-AI Collaborative Triage (`skillaudit triage` & `skillaudit signoff`)**: Bi-directional workflow allowing human lead auditors to review AI proposals, resolve unknowns, and issue certified audit opinions (WTP, WDP, Adverse, Disclaimer).
38: 
39: ## When to Use This Skill
40: Activate this skill whenever the user asks to:
41: - Audit, inspect, or verify documents, contracts, spreadsheets, transaction logs, or complete dossiers.
42: - Reconcile multi-document transactions (3-Way Matching: Contract vs BAST vs Invoice vs Payment).
43: - Detect Segregation of Duties (SoD) violations or Delegation of Authority (DoA) limit breaches.
44: - Formulate findings adhering to international 5C standards (Condition, Criteria, Cause, Consequence, Recommendation).
45: - Manage the Ledger of Unknowns, inspect Evidence Bundles, or conduct Human-AI collaborative triage.
46: - Generate formal Laporan Hasil Audit (LHA), Kertas Kerja Audit (KKA), or offline HTML dashboards.
47: 
48: ## Core Trust Boundaries
49: - **Zero Hallucination Grounding**: Every finding must quote verifiable verbatim source text with exact page/locator coordinates.
50: - **Strict 5C Format**: Every issue must have clear Condition, Criteria, Cause, Consequence, and Recommendation.
51: - **Tamper-Evident Integrity**: Every document is bound by cryptographic SHA-256 digests.
52: 
53: ## CLI Execution
54: ```bash
55: # 1. Audit full dossier with 5-pillar & REA analysis
56: skillaudit dossier path/to/dossier_folder/ --format all
57: 
58: # 2. Run 3-Way Matching cross-check
59: skillaudit cross-check contract.docx bast.pdf invoice.xlsx
60: 
61: # 3. Inspect Unknowns Ledger & Audit Obligations
62: skillaudit unknowns output/audit_pack.yaml
63: skillaudit obligations output/audit_pack.yaml
64: 
65: # 4. Export & verify cryptographic Evidence Bundle
66: skillaudit bundle output/audit_pack.yaml -o evidence_bundle.zip
67: skillaudit verify-bundle output/audit_pack.yaml
68: 
69: # 5. Interactive Human-AI Triage & Formal Sign-Off
70: skillaudit triage output/audit_pack.yaml
71: skillaudit signoff output/audit_pack.yaml --name "Lead Auditor" --opinion "WDP"
72: 
73: # 6. Deterministic CI/CD verification gate
74: skillaudit verify output/audit_pack.yaml --strict
75: ```
76: 
77: ## Detailed Reference Knowledge
78: - Consult `references/coso-internal-controls-guide.md` for COSO 17 Principles and control testing.
79: - Consult `references/iso31000-risk-management-guide.md` for 5x5 ERM Heatmap methodology.
80: - Consult `references/governance-doa-sod-guide.md` for DoA threshold matrices and SoD conflict rules.
81: - Consult `references/business-processes-audit-guide.md` for P2P, O2C, R2R, and H2R audit procedures.
82: - Consult `references/itgc-technical-audit-guide.md` for ITGC domains and cryptographic hash validation.
83: - Consult `references/5c-audit-finding-methodology.md` for international 5C finding formulation.


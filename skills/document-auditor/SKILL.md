---
name: document-auditor
description: Universal enterprise auditor capable of auditing any business process, technical ITGC, governance policy, internal controls, risk management, or regulatory domain (Segala Medan) with 5C findings, Benford forensic analysis, REA evidence ledgers, and Human-AI collaboration.
---

# Auditor-Anything (Universal Document Auditor) — AI Agent Skill

This skill equips the AI agent with a universal, multi-terrain operational doctrine to audit **any document, spreadsheet, system log, contract, or dossier across any domain or industry ("Segala Medan")**.

---

## 1. Universal Terrain Capabilities ("Segala Medan")

The engine automatically classifies and adapts audit procedures across 12+ operational domains:

1. **Procurement & Contracting (`PROCUREMENT`)**:
   - 3-Way Matching (PO vs. BAST vs. Invoice vs. Payment).
   - Perpres No. 16/2018 jo Perpres 12/2021 & LKPP procurement guidelines.
   - Tender collusion detection (bid rigging), split transactions, vendor cartel indicators.
2. **Financial & Accounting (`FINANCIAL`)**:
   - SAK / PSAK / IFRS compliance and cut-off testing.
   - General Ledger to Subledger reconciliations (AR/AP/Inventory).
   - Monthly bank statement reconciliation, unrecorded disbursements, and lapping/kiting detection.
3. **Public Sector & Government (`GOVERNMENT`)**:
   - Standar Akuntansi Pemerintahan (SAP / PP 71/2010), UU Keuangan Negara No. 17/2003.
   - DPA/RKA budget cap monitoring and SiLPA variance analysis.
   - Verification of SPP, SPM, SP2D, and BAP (Berita Acara Pembayaran).
4. **Healthcare & Hospital Billing (`HEALTHCARE`)**:
   - BPJS Kesehatan anti-fraud guidelines, Permenkes No. 24/2022 (Rekam Medis).
   - ICD-10 and INA-CBG upcoding detection, double billing, phantom billing.
   - Controlled narcotics/psychotropics register reconciliation (SIPNAP) and patient informed consent.
5. **Human Resources & Payroll (`HR_PAYROLL`)**:
   - UU No. 6/2023 (Cipta Kerja), PP 35/2021 (PKWT & PHK), PP 36/2021 (Pengupahan).
   - Ghost employee detection (duplicate bank accounts, duplicate NIK, post-resignation pay).
   - Overtime limits (max 4 hrs/day, 18 hrs/week), BPJS TK/Kes contributions, and PPh 21 TER calculations.
6. **Supply Chain & Operational Logistics (`SUPPLY_CHAIN`)**:
   - PSAK 14 (Persediaan) and Warehouse Management System (WMS) standards.
   - Physical Stock Opname reconciliation (BASO discrepancy tolerance $\le 2\%$).
   - Dead-stock and slow-moving aging ($> 180$ days), negative inventory balances, unauthorized write-offs.
7. **Forensic Investigation & Anti-Fraud (`FORENSIC_FRAUD`)**:
   - Benford's Law first-digit digital analysis (Nigrini 2012, ISA 240 / SA 240).
   - ACFE Fraud Tree, kickbacks, related-party concealment, weekend/holiday journal entries.
   - ISO 37001:2016 Sistem Manajemen Anti Penyuapan (SMAP) & Pakta Integritas.
8. **Cybersecurity & IT Controls (`IT_SECURITY`)**:
   - ISO/IEC 27001:2022, COBIT 2019, NIST CSF, and UU PDP No. 27/2022.
   - IT General Controls (ITGC): User Access Reviews, MFA, CAB Change Management, Backup Restoration testing.
   - Prevention of plaintext credentials, token leaks, and shared privileged accounts.
9. **Taxation & Customs (`TAX_CUSTOMS`)**:
   - UU HPP No. 7/2021, statutory PPN 11%, withholding tax (PPh 21, 23, 4(2), 25).
   - e-Faktur QR code verification, fictitious invoice detection, customs import/export (PIB/PEB).
10. **Banking, Fintech & AML (`BANKING_FINTECH`)**:
    - POJK APU-PPT (Anti-Pencucian Uang & Pencegahan Pendanaan Terorisme), UU No. 8/2010 TPPU.
    - Customer Due Diligence (CDD), Enhanced Due Diligence (EDD), and smurfing/structuring detection.
    - Financial soundness ratios (CAR, NPL, LDR, NIM, BOPO).
11. **ESG & Sustainability (`ESG_SUSTAINABILITY`)**:
    - POJK No. 51/POJK.03/2017 (Keuangan Berkelanjutan), UU No. 32/2009 (Lingkungan Hidup).
    - Scope 1, 2, 3 carbon emission verification, greenwashing detection.
    - Hazardous waste (Limbah B3) manifests and mandatory CSR/TJSL realization.
12. **Legal & Contractual Compliance (`LEGAL_CONTRACT`)**:
    - KUHPerdata perikatan, SLA compliance, penalty clauses, liability caps, dispute resolution.

---

## 2. Advanced Mathematical Forensics: Benford's Law

The skill incorporates **Nigrini (2012) Digital Analysis** to uncover manufactured numbers, manipulated accounting entries, and fictitious expenses:
- Expected digit distribution: $P(d) = \log_{10}(1 + 1/d)$ for $d \in \{1 \dots 9\}$.
- Mean Absolute Deviation (MAD):
  $$\text{MAD} = \frac{1}{9} \sum_{d=1}^{9} \left| \frac{N(d)}{N_{total}} - P_{exp}(d) \right|$$
  - $\text{MAD} \le 0.006$: *Close Conformity*
  - $0.006 < \text{MAD} \le 0.012$: *Acceptable Conformity*
  - $0.012 < \text{MAD} \le 0.015$: *Marginally Acceptable*
  - $\text{MAD} > 0.015$: *Non-Conforming* $\rightarrow$ Automatically flags anomalous digits and triggers **100% substantive forensic testing**!

---

## 3. Reverse-Engineering Forensics (`morluto/rea` Integration)

1. **Untrusted Provenance Boundary**:
   All audited files are tagged `_meta.provenance.untrusted_content = True` to isolate documents from executing instructions or hijacking LLM agent prompts.
2. **Ledger of Unknowns & Inquiries (`UnknownsEngine`)**:
   Evidentiary gaps are never assumed or hallucinated; they are registered into the Unknowns Ledger (`OPEN` $\rightarrow$ `RESOLVED` / `WAIVED`).
3. **Reconstruction Obligation Ledger (`ObligationEngine`)**:
   Statutory and domain-specific regulations are tracked as mandatory obligations, yielding a quantitative compliance coverage score.
4. **Cryptographic Evidence Bundles (`evidence_bundle`)**:
   Every document, finding, and unknown is bound to deterministic SHA-256 digests. `skillaudit verify-bundle` detects any post-audit document tampering.

---

## 4. Human-AI Collaborative Triage Workflow

```mermaid
flowchart LR
    A["AI Automated Audit\n(skillaudit audit)"] --> B["Evidence Bundle &\n5C Findings Draft"]
    B --> C["Human-in-the-Loop Triage\n(skillaudit triage / Web UI)"]
    C --> D["Resolve Unknowns &\nAdjust Risk"]
    D --> E["Formal Auditor Sign-Off\n(WTP / WDP / Adverse / Disclaimer)"]
    E --> F["Certified Deliverables\n(LHA + Evidence ZIP)"]
```

---

## 5. CLI Execution Reference

```bash
# 1. Universal Audit Across Any Domain
skillaudit audit path/to/dossier/ --output output/ --format all

# 2. Inspect Detected Audit Terrain
skillaudit terrain path/to/dossier/

# 3. Run Forensic Benford's Law Digital Analysis
skillaudit benford output/audit_pack.yaml

# 4. List All Universal Domain Profiles & Standards
skillaudit profiles

# 5. Review Unknowns & Statutory Obligations
skillaudit unknowns output/audit_pack.yaml
skillaudit obligations output/audit_pack.yaml

# 6. Verify Cryptographic Evidence Integrity (Tamper Detection)
skillaudit verify-bundle output/audit_pack.yaml

# 7. Interactive Human-AI Triage & Formal Sign-Off
skillaudit triage output/audit_pack.yaml
skillaudit signoff output/audit_pack.yaml --name "Lead Auditor, CPA" --opinion "WTP"
```

---

## 6. Zero-Hallucination Grounding Rule
Every finding generated by this skill must include:
- Verbatim quote (`quote_anchor`) from the audited source document.
- Explicit page/sheet/line locator.
- Complete 5C structure: **Condition**, **Criteria**, **Cause**, **Consequence**, and **Recommendation**.

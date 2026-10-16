---
name: document-auditor
description: Comprehensive document and audit dossier analyzer. Performs 3-way matching, arithmetic and tax verification, compliance checklist audits, and generates 5C audit findings backed by verbatim evidence quotes.
---

# Document Auditor — AI Agent Skill

This skill equips the agent to perform forensic, compliance, and procedural audits on financial dossiers, procurement records, contracts, spreadsheets, and administrative documents.

## When to Use This Skill
Activate this skill whenever the user asks to:
- Audit, verify, or review documents, dossiers, contracts, invoices, or financial records.
- Conduct 3-Way Matching (reconciling Contract/PO vs BAST/Goods Receipt vs Invoices vs Bank Proofs).
- Verify mathematical accuracy in tables, tax calculations (PPN 11%, PPh), and totals.
- Check compliance against procurement regulations (Perpres PBJ), ISO standards, or SOPs.
- Formulate standard 5C Audit Findings (Condition, Criteria, Cause, Consequence, Recommendation).
- Generate formal Laporan Hasil Audit (LHA), Kertas Kerja Audit (KKA), or interactive HTML audit dashboards.

## Core Principles & Trust Boundaries
1. **Zero Hallucination / Verifiable Grounding**:
   Every audit finding MUST cite the exact document name, section/page locator, and a verbatim quote. Uncited allegations are rejected.
2. **Standard 5C Audit Structure**:
   - **Condition (Kondisi)**: Factual reality observed in the document.
   - **Criteria (Kriteria)**: Applicable legal, policy, or contractual standard.
   - **Cause (Sebab)**: Root cause why the condition deviated from criteria.
   - **Consequence (Akibat)**: Financial, legal, or operational impact.
   - **Recommendation (Rekomendasi)**: Actionable, preventive corrective steps.
3. **Multi-Way Cross Reconciliation**:
   Trace values, dates, and parties across the complete dossier:
   `Contract/PO Date <= Delivery/BAST Date <= Invoice Date <= Payment Date`

## Using the CLI Tool
The repository includes the `skillaudit` CLI:

```bash
# 1. Audit a single document
skillaudit doc path/to/invoice.pdf --format all

# 2. Audit an entire dossier folder or ZIP bundle
skillaudit dossier path/to/procurement_dossier/ --format all

# 3. Explicit cross-check between specific files
skillaudit cross-check contract.docx bast.pdf invoice.xlsx

# 4. Deterministic quality verification (CI/CD gate)
skillaudit verify output/audit_pack.yaml --strict

# 5. Shareable bundle (Offline interactive HTML + ZIP)
skillaudit share output/audit_pack.yaml
```

## Reference Documentation
- Consult `references/5c-audit-finding-methodology.md` for standard 5C writing techniques.
- Consult `references/3-way-matching-guide.md` for 3-way reconciliation rules.
- Consult `references/audit-sampling-techniques.md` for sampling methods on large ledgers.

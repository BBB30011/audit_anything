"""Exporter to produce Claude Code, Cursor, and Antigravity compatible Agent Skills."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from skill_audit.models import AuditPack, slugify


class SkillExporter:
    """Exports an AuditPack or auditing capabilities into a standard agent skill directory."""

    def export(
        self,
        pack: AuditPack,
        output_dir: str | Path,
    ) -> Path:
        """Create a complete SKILL.md directory bundle based on an AuditPack."""
        slug = slugify(pack.title)
        skill_dir = Path(output_dir) / slug
        skill_dir.mkdir(parents=True, exist_ok=True)

        refs_dir = skill_dir / "references"
        assets_dir = skill_dir / "assets"
        scripts_dir = skill_dir / "scripts"
        for d in (refs_dir, assets_dir, scripts_dir):
            d.mkdir(parents=True, exist_ok=True)

        # 1. SKILL.md
        (skill_dir / "SKILL.md").write_text(
            self._render_skill_md(pack), encoding="utf-8"
        )

        # 2. references/
        (refs_dir / "5c-audit-methodology.md").write_text(
            self._render_5c_reference(), encoding="utf-8"
        )
        (refs_dir / "3-way-matching-guide.md").write_text(
            self._render_3way_matching_reference(), encoding="utf-8"
        )

        # 3. assets/
        pack.to_yaml(assets_dir / "audit_pack.yaml")

        # 4. scripts/
        (scripts_dir / "run_audit.py").write_text(
            self._render_audit_script(), encoding="utf-8"
        )

        return skill_dir

    def install_to_agent(
        self,
        source_skill_dir: Path,
        target_platform: str = "antigravity",
    ) -> Path:
        """Install skill directory to the specified AI Agent's global skills catalog."""
        home = Path.home()
        if target_platform == "antigravity":
            target_base = home / ".gemini" / "config" / "plugins" / "antigravity-skills-manager" / "skills"
            if not target_base.exists():
                target_base = home / ".gemini" / "antigravity-cli" / "skills"
        elif target_platform == "claude":
            target_base = home / ".claude" / "skills"
        elif target_platform == "cursor":
            target_base = Path.cwd() / ".agents" / "skills"
        else:
            target_base = Path(target_platform)

        target_base.mkdir(parents=True, exist_ok=True)
        dest = target_base / source_skill_dir.name

        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(source_skill_dir, dest)
        return dest

    def _render_skill_md(self, pack: AuditPack) -> str:
        slug = slugify(pack.title)
        return f"""---
name: {slug}
description: Specialized AI agent skill for comprehensive document and audit dossier verification, 3-way matching, and 5C findings analysis.
---

# {pack.title} — Document Audit Skill

This skill equips AI agents to conduct rigorous, multi-document forensic and compliance audits on financial statements, procurement dossiers, legal contracts, and administrative records.

## When to Use This Skill
- Auditing procurement dossiers (PO / SPK, BAST, Invoices, Tax Invoices, Bank Receipts).
- Validating financial calculations, tax rates (PPN 11%, PPh), and totals.
- Conducting 3-Way Matching and cross-document reconciliation.
- Evaluating compliance against internal SOPs, ISO standards, or statutory regulations.
- Generating formal 5C Audit Finding matrices (Condition, Criteria, Cause, Consequence, Recommendation).

## Core Capabilities
1. **Multi-Source Ingestion**: Ingests PDFs, Excel spreadsheets, CSVs, Word documents, and full dossiers.
2. **Deterministic Evidence Grounding**: Enforces strict trust boundaries where every finding must cite a verbatim quote and exact document locator.
3. **Automated 3-Way Reconciliation**: Compares line items, totals, dates, and vendor details across multiple documents.
4. **Chronology & Anomaly Detection**: Uncovers premature billing, post-factum contracts, split purchases, and missing statutory stamps.

## Standard Audit Workflow
1. **Dossier Inventory**: Catalog all submitted documents and assign their role (`contract`, `goods_receipt`, `invoice`, `payment_proof`).
2. **Substantive Arithmetic Verification**: Recalculate quantity * unit price, check PPN 11%, check subtotals and grand totals.
3. **Cross-Document Matching**: Check that invoice values do not exceed contract agreements and that BAST was issued prior to invoice date.
4. **Compliance Checklist Evaluation**: Test mandatory statutory clauses and administrative attachments.
5. **Formulate 5C Findings**: Write findings strictly adhering to Condition, Criteria, Cause, Consequence, and Recommendation.

## Quick CLI Execution
Run the standalone audit script directly:
```bash
python scripts/run_audit.py /path/to/dossier_folder
```

See `references/` for detailed 5C guidelines and 3-Way Matching protocols.
"""

    @staticmethod
    def _render_5c_reference() -> str:
        return """# 5C Audit Finding Methodology

The 5C Framework is the international gold standard for formulating audit findings (IIA & BPK standard):

1. **Condition (Kondisi)**:
   - What is the factual state observed during testing?
   - Must be objective, specific, and backed by verifiable quotes and document references.

2. **Criteria (Kriteria)**:
   - What standard, regulation, policy, contract clause, or benchmark should have been followed?
   - Cite specific law articles, SOP numbers, or contract clauses.

3. **Cause (Sebab)**:
   - Why did the deviation happen?
   - Identifies the root cause (e.g., absence of automated validation, inadequate training, lack of segregation of duties).

4. **Consequence / Impact (Akibat / Dampak)**:
   - What is the financial, operational, reputational, or legal exposure?
   - Quantify financial losses or penalties where possible.

5. **Corrective Action / Recommendation (Rekomendasi)**:
   - Actionable, constructive, and cost-effective steps to resolve the immediate finding and prevent recurrence.
"""

    @staticmethod
    def _render_3way_matching_reference() -> str:
        return """# 3-Way Matching Protocol for Procurement & Financial Audits

3-Way Matching is the fundamental internal control verifying that a company pays only for goods/services that were officially authorized and verified:

## The Triad:
1. **Purchase Order / SPK (Authorization)**: Authorizes items, quantities, agreed prices, and terms.
2. **Goods Receipt / BAST (Verification)**: Confirms that goods/services were actually delivered in full and satisfactory quality.
3. **Invoice (Billing)**: Vendor's bill specifying items, unit prices, taxes, and bank account.

## Mandatory Reconciliation Rules:
- **Quantity Match**: Invoiced Qty <= Received Qty in BAST.
- **Price Match**: Invoiced Unit Price == Authorized Price in SPK.
- **Date Sequencing**: SPK Date <= BAST Date <= Invoice Date <= Payment Date.
- **Vendor Identity**: Vendor name and Tax ID (NPWP) on Invoice must match the contract signatory.
"""

    @staticmethod
    def _render_audit_script() -> str:
        return """#!/usr/bin/env python3
import sys
from pathlib import Path
from skill_audit.engine import AuditEngine
from skill_audit.exporters import ReportExporter, WebExporter

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_audit.py <path_to_document_or_dossier>")
        sys.exit(1)

    target = sys.argv[1]
    engine = AuditEngine()
    pack = engine.audit(target)

    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)

    report_exp = ReportExporter()
    report_exp.export_report(pack, out_dir / "audit_report.md")

    web_exp = WebExporter()
    web_exp.export(pack, out_dir / "audit_dashboard.html")

    print(f"Audit completed: {len(pack.findings)} findings found.")
    print(f"Report: {out_dir / 'audit_report.md'}")
    print(f"Dashboard: {out_dir / 'audit_dashboard.html'}")

if __name__ == "__main__":
    main()
"""

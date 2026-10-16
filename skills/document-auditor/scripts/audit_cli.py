#!/usr/bin/env python3
"""Standalone CLI runner for Document Auditor Skill."""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path if running directly
proj_root = Path(__file__).resolve().parent.parent.parent.parent
if str(proj_root) not in sys.path:
    sys.path.insert(0, str(proj_root))

from skill_audit.engine import AuditEngine
from skill_audit.exporters import ReportExporter, WebExporter


def main():
    if len(sys.argv) < 2:
        print("Usage: python audit_cli.py <target_file_or_dossier_dir> [--output <output_dir>]")
        sys.exit(1)

    target_path = Path(sys.argv[1])
    out_dir = Path("output")
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            out_dir = Path(sys.argv[idx + 1])

    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Menjalankan audit atas: {target_path}")
    engine = AuditEngine()
    pack = engine.audit(target_path)

    report_exp = ReportExporter()
    report_file = out_dir / "audit_report.md"
    kka_file = out_dir / "kertas_kerja_audit.md"
    report_exp.export_report(pack, report_file)
    report_exp.export_working_papers(pack, kka_file)

    web_exp = WebExporter()
    web_file = out_dir / "audit_dashboard.html"
    web_exp.export(pack, web_file)

    pack_file = out_dir / "audit_pack.yaml"
    pack.to_yaml(pack_file)

    print(f"[+] Audit Selesai!")
    print(f"    - Total Temuan    : {len(pack.findings)}")
    print(f"    - Skor Kepatuhan  : {pack.metrics.compliance_score:.1f}%")
    print(f"    - Laporan (LHA)   : {report_file}")
    print(f"    - Kertas Kerja    : {kka_file}")
    print(f"    - Dasbor Web      : {web_file}")
    print(f"    - AuditPack YAML  : {pack_file}")


if __name__ == "__main__":
    main()

"""CSV exporter for findings and working papers."""

from __future__ import annotations

import csv
from pathlib import Path

from skill_audit.models import AuditPack


class CSVExporter:
    """Exports findings and working papers to standard CSV format."""

    def export_findings(self, pack: AuditPack, output_file: str | Path) -> Path:
        out_path = Path(output_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(out_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "ID Temuan",
                "Tingkat Risiko",
                "Kategori",
                "Judul Temuan",
                "Kondisi (Condition)",
                "Kriteria (Criteria)",
                "Sebab (Cause)",
                "Akibat (Consequence)",
                "Rekomendasi (Recommendation)",
                "Bukti Kutipan",
                "Batas Waktu (Hari)",
            ])
            for item in pack.findings:
                ev_str = " | ".join(f"{e.document} ({e.locator}): {e.excerpt}" for e in item.evidence)
                writer.writerow([
                    item.id,
                    item.risk_level.value.upper(),
                    item.category,
                    item.title,
                    item.condition,
                    item.criteria,
                    item.cause,
                    item.consequence,
                    item.recommendation,
                    ev_str,
                    item.remediation_deadline_days,
                ])

        return out_path

    def export_working_papers(self, pack: AuditPack, output_file: str | Path) -> Path:
        out_path = Path(output_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(out_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Ref KKA",
                "Prosedur Pemeriksaan",
                "Dokumen Diuji",
                "Hasil Pengujian",
                "Catatan",
                "Ref Temuan",
            ])
            for w in pack.working_papers:
                writer.writerow([
                    w.ref_no,
                    w.procedure,
                    w.document_ref,
                    w.result.value.upper(),
                    w.notes,
                    w.finding_ref or "",
                ])

        return out_path

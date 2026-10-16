"""Compliance framework and checklist analyzer for audit standards."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from skill_audit.grounding import normalize_evidence
from skill_audit.models import (
    AuditDocument,
    AuditStatus,
    EvidenceCitation,
    Finding5C,
    RiskLevel,
    WorkingPaperRow,
)


class ComplianceAnalyzer:
    """Evaluates audit documents against compliance frameworks and standard checklists."""

    def analyze(
        self,
        documents: list[AuditDocument],
        checklist_config: dict[str, Any] | str | Path | None = None,
    ) -> tuple[list[Finding5C], list[WorkingPaperRow], float]:
        """Run compliance checklist audit.

        Returns (findings, working_papers, compliance_score_percentage).
        """
        checklist = self._resolve_checklist(checklist_config)
        items = checklist.get("items", [])
        framework_name = checklist.get("name", "Audit Kepatuhan Dokumen")

        findings: list[Finding5C] = []
        working_papers: list[WorkingPaperRow] = []

        passed_count = 0
        total_evaluable = len(items)
        combined_text = "\n\n".join(f"[{d.name}]\n{d.content}" for d in documents)

        for idx, item in enumerate(items, 1):
            ref_no = item.get("ref_no", f"KKA-{idx:02d}")
            title = item.get("title", f"Pemeriksaan Kepatuhan {idx}")
            criteria = item.get("criteria", "Standar Kepatuhan Operasional")
            keywords = [k.lower() for k in item.get("keywords", [])]
            is_mandatory = item.get("mandatory", True)
            risk_level = RiskLevel(item.get("risk_level", "medium"))
            target_role = item.get("target_role")

            # Filter relevant documents
            eval_docs = [d for d in documents if d.role_in_dossier == target_role] if target_role else documents
            if not eval_docs:
                eval_docs = documents

            # Check if keywords are matched in content
            matched_evidence: list[EvidenceCitation] = []
            found = False

            for doc in eval_docs:
                content_lower = doc.content.lower()
                matched_kw = [k for k in keywords if k in content_lower]
                if matched_kw:
                    found = True
                    # Grab excerpt around the first keyword
                    kw_first = matched_kw[0]
                    pos = content_lower.find(kw_first)
                    start_pos = max(0, pos - 40)
                    end_pos = min(len(doc.content), pos + len(kw_first) + 60)
                    excerpt = normalize_evidence(doc.content[start_pos:end_pos])
                    matched_evidence.append(
                        EvidenceCitation(
                            document=doc.name,
                            locator="Verifikasi Klausul",
                            excerpt=excerpt,
                        )
                    )
                    break

            if found:
                status = AuditStatus.PASS
                passed_count += 1
                notes = f"Sesuai. Ditemukan pemenuhan klausul: {', '.join(matched_kw)}."
            else:
                status = AuditStatus.FAIL if is_mandatory else AuditStatus.WARNING
                notes = f"Klausul/elemen audit '{title}' tidak ditemukan dalam berkas."

                # If failed and mandatory, record a finding
                if is_mandatory:
                    finding = Finding5C(
                        id=f"FND-COMP-{idx:03d}",
                        title=f"Ketiadaan / Ketidakpatuhan Elemen: {title}",
                        risk_level=risk_level,
                        category="Kepatuhan Regulasi & Standar",
                        condition=f"Dalam pengujian berkas, tidak ditemukan elemen/ketentuan '{title}' pada dokumen yang diaudit.",
                        criteria=criteria,
                        cause="Dokumen standar belum memuat klausul proteksi atau berkas pendukung wajib belum dilampirkan.",
                        consequence=item.get("consequence", "Potensi sengketa hukum atau ketidakpatuhan terhadap standar tata kelola yang baik."),
                        recommendation=item.get("recommendation", f"Lengkapi dan masukkan klausul/dokumen '{title}' dalam berkas transaksi."),
                        evidence=[],
                        tags=["compliance", "checklist", framework_name.lower().replace(" ", "-")],
                    )
                    findings.append(finding)

            working_papers.append(
                WorkingPaperRow(
                    ref_no=ref_no,
                    procedure=f"Pemeriksaan Kepatuhan: {title}",
                    document_ref=", ".join(d.name for d in eval_docs),
                    test_performed=f"Pengujian keberadaan klausul/bukti: {', '.join(keywords) if keywords else title}",
                    result=status,
                    notes=notes,
                    evidence=matched_evidence,
                    finding_ref=f"FND-COMP-{idx:03d}" if status == AuditStatus.FAIL else None,
                )
            )

        compliance_score = (passed_count / total_evaluable * 100.0) if total_evaluable > 0 else 100.0
        return findings, working_papers, compliance_score

    def _resolve_checklist(self, config: dict[str, Any] | str | Path | None) -> dict[str, Any]:
        if isinstance(config, dict):
            return config
        elif isinstance(config, (str, Path)) and Path(config).exists():
            content = Path(config).read_text(encoding="utf-8")
            return yaml.safe_load(content) or {}
        else:
            # Default to General Procurement & Financial Compliance Checklist
            return self._default_procurement_checklist()

    @staticmethod
    def _default_procurement_checklist() -> dict[str, Any]:
        return {
            "name": "Audit Standar Pengadaan Barang & Jasa (PBJ)",
            "items": [
                {
                    "ref_no": "KKA-PBJ-01",
                    "title": "Dokumen Kontrak / SPK / Surat Pesanan Sah",
                    "criteria": "Perpres Pengadaan & SOP Pengadaan: Setiap transaksi barang/jasa wajib memiliki dasar perikatan/kontrak sah.",
                    "keywords": ["spk", "surat perintah kerja", "kontrak", "perjanjian", "purchase order"],
                    "target_role": "contract",
                    "mandatory": True,
                    "risk_level": "critical",
                    "consequence": "Belanja tanpa dasar ikatan hukum mengikat.",
                    "recommendation": "Terbitkan SPK/Kontrak sebelum pekerjaan dimulai.",
                },
                {
                    "ref_no": "KKA-PBJ-02",
                    "title": "Berita Acara Serah Terima (BAST) / Surat Penerimaan",
                    "criteria": "SOP Pembayaran: Serah terima barang/jasa wajib diverifikasi oleh pejabat pemeriksa hasil pekerjaan.",
                    "keywords": ["bast", "serah terima", "berita acara", "delivery note", "diterima dengan baik"],
                    "target_role": "goods_receipt",
                    "mandatory": True,
                    "risk_level": "critical",
                    "consequence": "Risiko pembayaran atas pekerjaan fiktif atau belum selesai.",
                    "recommendation": "Lampirkan BAST sah bertanda tangan pihak penyedia dan penerima.",
                },
                {
                    "ref_no": "KKA-PBJ-03",
                    "title": "Faktur Pajak / Bukti Potong Pajak",
                    "criteria": "UU PPN & PPh: Penyerahan BKP/JKP wajib disertai penerbitan Faktur Pajak sah.",
                    "keywords": ["faktur pajak", "ppn", "pajak pertambahan nilai", "kode faktur", "djp"],
                    "mandatory": True,
                    "risk_level": "high",
                    "consequence": "Sanksi denda pajak dan tidak dapat dikreditkannya PPN masukan.",
                    "recommendation": "Mintakan Faktur Pajak elektronik (e-Faktur) resmi dari penyedia.",
                },
                {
                    "ref_no": "KKA-PBJ-04",
                    "title": "Klausul Sanksi / Denda Keterlambatan",
                    "criteria": "Klausul Standar Kontrak: Wajib memuat denda keterlambatan (1 mil/hari keterlambatan).",
                    "keywords": ["denda", "keterlambatan", "sanksi", "permil", "1/1000"],
                    "target_role": "contract",
                    "mandatory": True,
                    "risk_level": "medium",
                    "consequence": "Pemberi kerja kehilangan hak klaim kompensasi jika penyedia terlambat menyerahkan hasil pekerjaan.",
                    "recommendation": "Cantumkan klausul denda keterlambatan secara eksplisit dalam naskah perjanjian.",
                },
                {
                    "ref_no": "KKA-PBJ-05",
                    "title": "Klausul Keadaan Kahar (Force Majeure)",
                    "criteria": "KUHPerdata Pasal 1244-1245 & Standar Kontrak: Klausul penanganan kondisi luar biasa di luar kendali para pihak.",
                    "keywords": ["force majeure", "keadaan kahar", "bencana alam", "keadaan memaksa"],
                    "target_role": "contract",
                    "mandatory": False,
                    "risk_level": "low",
                    "consequence": "Ketidakpastian alokasi risiko saat terjadi bencana atau kebijakan darurat pemerintah.",
                    "recommendation": "Tambahkan klausul Force Majeure yang mengatur prosedur notifikasi dan konsekuensi perikatan.",
                },
                {
                    "ref_no": "KKA-PBJ-06",
                    "title": "Klausul Penyelesaian Perselisihan (Dispute Resolution)",
                    "criteria": "Standar Kontrak Komersial: Penentuan forum penyelesaian sengketa (Musyawarah, BANI, atau Pengadilan Negeri).",
                    "keywords": ["perselisihan", "sengketa", "pengadilan negeri", "arbitrase", "musyawarah mufakat"],
                    "target_role": "contract",
                    "mandatory": True,
                    "risk_level": "medium",
                    "consequence": "Ketidakjelasan yurisdiksi dan mekanisme hukum jika timbul sengketa wanprestasi.",
                    "recommendation": "Tentukan secara tegas domisili hukum penyelesaian sengketa.",
                },
            ],
        }

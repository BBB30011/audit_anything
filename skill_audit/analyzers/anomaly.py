"""Anomaly and red-flag detector for document and dossier audits."""

from __future__ import annotations

import re
from typing import Any

from skill_audit.grounding import normalize_evidence
from skill_audit.models import (
    AuditDocument,
    EvidenceCitation,
    Finding5C,
    RiskLevel,
)


class AnomalyDetector:
    """Detects fraud red flags, transaction splitting, missing statutory stamps, and administrative gaps."""

    def analyze(self, documents: list[AuditDocument]) -> list[Finding5C]:
        findings: list[Finding5C] = []
        finding_idx = 1

        for doc in documents:
            # 1. Missing Stamp Duty (Meterai) for transactions > Rp 5.000.000
            stamp_finding = self._check_stamp_duty(doc, finding_idx)
            if stamp_finding:
                findings.append(stamp_finding)
                finding_idx += 1

            # 2. Missing NPWP / Tax ID on invoices
            if doc.role_in_dossier in ["invoice", "contract"]:
                npwp_finding = self._check_tax_id(doc, finding_idx)
                if npwp_finding:
                    findings.append(npwp_finding)
                    finding_idx += 1

            # 3. Missing Authorized Signature / Approval
            sig_finding = self._check_signature_presence(doc, finding_idx)
            if sig_finding:
                findings.append(sig_finding)
                finding_idx += 1

        # 4. Check potential tender / procurement splitting across all invoices
        split_finding = self._check_transaction_splitting(documents, finding_idx)
        if split_finding:
            findings.append(split_finding)

        return findings

    def _check_stamp_duty(self, doc: AuditDocument, idx: int) -> Finding5C | None:
        """Check compliance with UU Bea Meterai No. 10/2020 for amounts > Rp 5.000.000."""
        amounts = doc.entities.get("amounts", [])
        if not amounts:
            return None

        max_amount = max(a["value"] for a in amounts if isinstance(a, dict) and "value" in a)
        if max_amount >= 5000000:
            content_lower = doc.content.lower()
            if not any(k in content_lower for k in ["meterai", "bea meterai", "e-meterai", "materai", "meterai elektronik"]):
                return Finding5C(
                    id=f"FND-ANOM-{idx:03d}",
                    title=f"Ketiadaan Bea Meterai pada Dokumen Bernilai Tinggi ({doc.name})",
                    risk_level=RiskLevel.MEDIUM,
                    category="Kepatuhan Administrasi & Perpajakan",
                    condition=(
                        f"Dokumen {doc.name} bernilai transaksi Rp {max_amount:,.0f} (>= Rp 5.000.000), "
                        f"namun tidak memuat keterangan atau pembubuhan Bea Meterai."
                    ),
                    criteria="UU Nomor 10 Tahun 2020 tentang Bea Meterai Pasal 3 ayat (2) (kewajiban meterai atas dokumen bernilai > Rp 5.000.000).",
                    cause="Kelalaian administrasi pembuatan kuitansi/perjanjian atau kurangnya pemahaman regulasi bea meterai terkini.",
                    consequence="Dokumen memiliki kelemahan alat bukti hukum perdata dan dapat dikenakan sanksi denda pemeteraian kemudian (200%).",
                    recommendation="Bubuhkan meterai tempel/e-meterai Rp 10.000 dan lakukan pemeteraian kemudian sesuai ketentuan Kantor Pos/DJP.",
                    evidence=[
                        EvidenceCitation(
                            document=doc.name,
                            locator="Nilai Dokumen",
                            excerpt=f"Nilai: Rp {max_amount:,.0f}",
                        )
                    ],
                    tags=["meterai", "stamp-duty", "compliance"],
                )
        return None

    def _check_tax_id(self, doc: AuditDocument, idx: int) -> Finding5C | None:
        """Check if Invoice or Contract has Tax ID / NPWP."""
        tax_ids = doc.entities.get("tax_ids", [])
        if not tax_ids:
            return Finding5C(
                id=f"FND-ANOM-{idx:03d}",
                title=f"Nomor Pokok Wajib Pajak (NPWP) Tidak Tercantum pada {doc.name}",
                risk_level=RiskLevel.MEDIUM,
                category="Kepatuhan Administrasi & Perpajakan",
                condition=f"Dokumen transaksi/perjanjian {doc.name} tidak mencantumkan NPWP penyedia/rekanan secara valid.",
                criteria="Peraturan Direktur Jenderal Pajak tentang Syarat Formal Faktur & Dokumen Tertentu yang Dipersamakan.",
                cause="Identitas perpajakan rekanan belum diintegrasikan ke dalam master data pengadaan/keuangan.",
                consequence="Potensi kendala pelaporan SPT Masa PPh/PPN dan risiko pengenaan tarif potong lebih tinggi (100% lebih tinggi bagi non-NPWP).",
                recommendation="Wajibkan pencantuman NPWP/NIK 16 digit pada setiap dokumen tagihan dan perjanjian rekanan.",
                evidence=[
                    EvidenceCitation(
                        document=doc.name,
                        locator="Identitas Rekanan",
                        excerpt=normalize_evidence(doc.content[:180]),
                    )
                ],
                tags=["npwp", "tax-id", "vendor-data"],
            )
        return None

    def _check_signature_presence(self, doc: AuditDocument, idx: int) -> Finding5C | None:
        """Check if document has evidence of signatures or approvals."""
        sigs = doc.entities.get("signatures_detected", [])
        if not sigs and doc.role_in_dossier in ["contract", "goods_receipt", "invoice"]:
            return Finding5C(
                id=f"FND-ANOM-{idx:03d}",
                title=f"Ketiadaan Pengesahan / Tanda Tangan Resmi pada {doc.name}",
                risk_level=RiskLevel.HIGH,
                category="Otorisasi & Keabsahan Dokumen",
                condition=f"Pada dokumen {doc.name} ({doc.role_in_dossier}) tidak terdeteksi adanya tanda tangan, paraf, atau pengesahan pejabat berwenang.",
                criteria="Kebijakan Otorisasi Dokumen Keuangan dan Pengadaan Barang/Jasa.",
                cause="Dokumen yang diserahkan masih berupa draf mentah (draft copy) atau file tanpa pengesahan basah/elektronik.",
                consequence="Dokumen cacat otorisasi sehingga tidak dapat dipertanggungjawabkan secara sah sebagai beban belanja.",
                recommendation="Minta dokumen bertanda tangan lengkap dan pastikan dokumen yang diarsip adalah naskah asli bertanda tangan sah.",
                evidence=[
                    EvidenceCitation(
                        document=doc.name,
                        locator="Halaman Penutup",
                        excerpt=normalize_evidence(doc.content[-200:]) if len(doc.content) > 200 else normalize_evidence(doc.content),
                    )
                ],
                tags=["signature", "authorization", "validity"],
            )
        return None

    def _check_transaction_splitting(self, documents: list[AuditDocument], idx: int) -> Finding5C | None:
        """Check if multiple invoices appear to be split just under statutory thresholds (e.g. 50jt or 200jt)."""
        invoices = [d for d in documents if d.role_in_dossier == "invoice"]
        if len(invoices) < 2:
            return None

        # Check values just below 50,000,000 (direct procurement threshold in Indonesia)
        split_candidates: list[str] = []
        for inv in invoices:
            amounts = inv.entities.get("amounts", [])
            for a in amounts:
                val = a["value"]
                # 45jt - 49.99jt is the classic split range
                if 45000000 <= val < 50000000:
                    split_candidates.append(f"{inv.name} (Rp {val:,.0f})")

        if len(split_candidates) >= 2:
            return Finding5C(
                id=f"FND-ANOM-{idx:03d}",
                title="Indikasi Pemecahan Paket Pengadaan (Split Purchasing)",
                risk_level=RiskLevel.CRITICAL,
                category="Indikasi Anomali & Fraud Risk",
                condition=(
                    f"Ditemukan {len(split_candidates)} invoice dengan nilai transaksi mendekati batas pagu Pengadaan Langsung "
                    f"(Rp 50.000.000): {', '.join(split_candidates)}."
                ),
                criteria="Perpres Nomor 16 Tahun 2018 jo Perpres Nomor 12 Tahun 2021 tentang Pengadaan Barang/Jasa Pemerintah Pasal 20 ayat (2) (Larangan memecah pengadaan untuk menghindari tender).",
                cause="Upaya menghindari prosedur lelang/tender kompetitif atau kemudahan administratif penunjukan langsung.",
                consequence="Pelanggaran regulasi pengadaan nasional dan potensi pemborosan keuangan negara/perusahaan akibat hilangnya persaingan harga wajar.",
                recommendation="Lakukan audit investigatif atas perencanaan kebutuhan barang/jasa dan konsolidasikan paket pengadaan sejenis di masa mendatang.",
                evidence=[
                    EvidenceCitation(
                        document=invoices[0].name,
                        locator="Rincian Nilai",
                        excerpt=split_candidates[0],
                    )
                ],
                tags=["split-purchase", "fraud-risk", "procurement"],
            )
        return None

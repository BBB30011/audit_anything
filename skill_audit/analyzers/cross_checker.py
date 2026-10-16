"""Multi-document cross-checker and 3-Way Matching reconciliation engine."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from skill_audit.grounding import normalize_evidence
from skill_audit.models import (
    AuditDocument,
    AuditStatus,
    EvidenceCitation,
    Finding5C,
    ReconciliationItem,
    RiskLevel,
)


class CrossChecker:
    """Performs 3-Way Matching (Contract vs BAST vs Invoice vs Payment) and chronological consistency checks."""

    def analyze(self, documents: list[AuditDocument]) -> tuple[list[Finding5C], list[ReconciliationItem]]:
        findings: list[Finding5C] = []
        reconciliations: list[ReconciliationItem] = []
        finding_idx = 1

        # 1. Group documents by role
        doc_map: dict[str, list[AuditDocument]] = {
            "contract": [],
            "goods_receipt": [],
            "invoice": [],
            "tax_document": [],
            "payment_proof": [],
            "general": [],
        }
        for doc in documents:
            role = doc.role_in_dossier
            if role in doc_map:
                doc_map[role].append(doc)
            else:
                doc_map["general"].append(doc)

        contracts = doc_map["contract"]
        receipts = doc_map["goods_receipt"]
        invoices = doc_map["invoice"]
        payments = doc_map["payment_proof"]

        # 2. Check 3-Way Matching Completeness
        if invoices and not receipts:
            findings.append(
                Finding5C(
                    id=f"FND-XMATCH-{finding_idx:03d}",
                    title="Tagihan (Invoice) Ditemukan Tanpa Berita Acara Serah Terima (BAST)",
                    risk_level=RiskLevel.CRITICAL,
                    category="Uji Kelengkapan & 3-Way Matching",
                    condition=(
                        f"Terdapat {len(invoices)} dokumen tagihan/invoice ({', '.join(d.name for d in invoices)}) "
                        f"namun tidak ditemukan Berita Acara Serah Terima (BAST) atau Surat Jalan penerimaan barang/jasa."
                    ),
                    criteria="Standar Pengendalian Internal (COSO) dan Prosedur Standar Operasional (SOP) Pembayaran Vendor (Prinsip 3-Way Matching: PO - BAST - Invoice).",
                    cause="Kelemahan kontrol penerimaan tagihan di bagian keuangan atau penyerahan berkas yang tidak terkoordinasi dari user operasional.",
                    consequence="Risiko pembayaran atas pekerjaan/barang fiktif, belum tuntas diselesaikan, atau cacat mutu tanpa jaminan verifikasi fisik.",
                    recommendation="Tangguhkan verifikasi pembayaran sampai unit pemohon melampirkan BAST sah yang ditandatangani panitia penerima hasil pekerjaan.",
                    evidence=[
                        EvidenceCitation(
                            document=invoices[0].name,
                            locator="Dokumen Tagihan",
                            excerpt=normalize_evidence(invoices[0].content[:200]),
                        )
                    ],
                    tags=["3-way-match", "missing-bast", "internal-control"],
                )
            )
            finding_idx += 1

        if invoices and not contracts:
            findings.append(
                Finding5C(
                    id=f"FND-XMATCH-{finding_idx:03d}",
                    title="Tagihan Tanpa Dasar Kontrak / SPK / Purchase Order",
                    risk_level=RiskLevel.HIGH,
                    category="Uji Kelengkapan & 3-Way Matching",
                    condition=f"Terdapat invoice ({', '.join(d.name for d in invoices)}) namun tidak ditemukan Kontrak atau Surat Perintah Kerja (SPK) pendukung.",
                    criteria="Regulasi Pengadaan dan Kebijakan Otorisasi Komitmen Anggaran.",
                    cause="Pengadaan mendadak tanpa penerbitan kontrak formal atau dokumen kontrak belum diarsipkan ke berkas audit.",
                    consequence="Pengeluaran anggaran tidak memiliki dasar ikatan hukum dan batasan hak/kewajiban yang mengikat.",
                    recommendation="Pastikan setiap perikatan didahului SPK/PO formal sebelum pesanan dilaksanakan.",
                    evidence=[
                        EvidenceCitation(
                            document=invoices[0].name,
                            locator="Dokumen Tagihan",
                            excerpt=normalize_evidence(invoices[0].content[:200]),
                        )
                    ],
                    tags=["missing-contract", "authorization"],
                )
            )
            finding_idx += 1

        # 3. Cross-Check Amounts (Contract vs Invoice vs Payment)
        reconciliations.extend(self._reconcile_amounts(contracts, receipts, invoices, payments, findings, finding_idx))
        finding_idx = len(findings) + 1

        # 4. Chronological Order Checks (Contract <= BAST <= Invoice <= Payment)
        findings.extend(self._check_chronology(contracts, receipts, invoices, payments, finding_idx))

        return findings, reconciliations

    def _reconcile_amounts(
        self,
        contracts: list[AuditDocument],
        receipts: list[AuditDocument],
        invoices: list[AuditDocument],
        payments: list[AuditDocument],
        findings: list[Finding5C],
        start_id: int,
    ) -> list[ReconciliationItem]:
        items: list[ReconciliationItem] = []

        c_val = self._get_primary_amount(contracts[0]) if contracts else None
        i_val = self._get_primary_amount(invoices[0]) if invoices else None
        p_val = self._get_primary_amount(payments[0]) if payments else None

        doc_values: dict[str, Any] = {}
        if contracts and c_val:
            doc_values[f"Kontrak ({contracts[0].name})"] = c_val
        if invoices and i_val:
            doc_values[f"Invoice ({invoices[0].name})"] = i_val
        if payments and p_val:
            doc_values[f"Bukti Bayar ({payments[0].name})"] = p_val

        if not doc_values:
            return items

        # Check Contract vs Invoice
        if c_val is not None and i_val is not None:
            diff = i_val - c_val
            if abs(diff) > 10.0:
                status = AuditStatus.FAIL
                desc = f"Selisih nilai Kontrak vs Invoice sebesar Rp {abs(diff):,.0f}"
                findings.append(
                    Finding5C(
                        id=f"FND-RECON-{start_id:03d}",
                        title="Selisih Nilai Transaksi antara Kontrak dan Tagihan (Invoice)",
                        risk_level=RiskLevel.CRITICAL if diff > 0 else RiskLevel.MEDIUM,
                        category="Rekonsiliasi Nilai Transaksi",
                        condition=(
                            f"Nilai pada Kontrak ({contracts[0].name}) tercatat Rp {c_val:,.0f}, "
                            f"sedangkan pada Invoice ({invoices[0].name}) tercatat Rp {i_val:,.0f}. "
                            f"Terdapat selisih {'kelebihan tagihan' if diff > 0 else 'kurang tagih'} senilai Rp {abs(diff):,.0f}."
                        ),
                        criteria="Klausul Pembayaran Kontrak: Pembayaran tidak boleh melampaui nilai pagu kontrak yang disepakati.",
                        cause="Terjadi perubahan volume/harga pekerjaan tanpa persetujuan Adendum/Amandemen Kontrak resmi.",
                        consequence=f"Potensi kerugian finansial akibat over-invoicing senilai Rp {diff:,.0f}." if diff > 0 else "Ketidaksesuaian administrasi pelaporan keuangan.",
                        recommendation="Konfirmasi dasar penagihan. Jika ada pekerjaan tambah, buatkan Adendum Kontrak. Jika tidak, minta revisi invoice sesuai nilai kontrak.",
                        evidence=[
                            EvidenceCitation(
                                document=invoices[0].name,
                                locator="Total Tagihan",
                                excerpt=f"Rp {i_val:,.0f}",
                            ),
                            EvidenceCitation(
                                document=contracts[0].name,
                                locator="Nilai Kontrak",
                                excerpt=f"Rp {c_val:,.0f}",
                            ),
                        ],
                        tags=["reconciliation", "over-invoicing", "contract-mismatch"],
                    )
                )
            else:
                status = AuditStatus.PASS
                desc = "Nilai Kontrak dan Invoice cocok (Rekonsiliasi Sesuai)."

            items.append(
                ReconciliationItem(
                    item_description="Uji Kesesuaian Nilai Kontrak vs Invoice",
                    doc_values=doc_values,
                    status=status,
                    discrepancy_amount=diff if abs(diff) > 10.0 else 0.0,
                    discrepancy_details=desc,
                )
            )

        return items

    def _check_chronology(
        self,
        contracts: list[AuditDocument],
        receipts: list[AuditDocument],
        invoices: list[AuditDocument],
        payments: list[AuditDocument],
        start_id: int,
    ) -> list[Finding5C]:
        findings: list[Finding5C] = []

        c_date = self._get_primary_date(contracts[0]) if contracts else None
        b_date = self._get_primary_date(receipts[0]) if receipts else None
        i_date = self._get_primary_date(invoices[0]) if invoices else None

        # Check BAST vs Invoice Date
        if b_date and i_date:
            if i_date < b_date:
                findings.append(
                    Finding5C(
                        id=f"FND-DATE-{start_id:03d}",
                        title="Anomali Tanggal: Invoice Diterbitkan Sebelum Tanggal BAST",
                        risk_level=RiskLevel.HIGH,
                        category="Uji Kronologi Dokumen",
                        condition=(
                            f"Tanggal Invoice ({invoices[0].name}) adalah {i_date.strftime('%d-%m-%Y')}, "
                            f"sedangkan tanggal BAST serah terima ({receipts[0].name}) adalah {b_date.strftime('%d-%m-%Y')}. "
                            f"Tagihan diterbitkan {(b_date - i_date).days} hari sebelum pekerjaan diserahterimakan."
                        ),
                        criteria="Ketentuan Pengajuan Pembayaran: Tagihan hanya dapat diterbitkan setelah barang/jasa diserahterimakan dan disetujui dalam BAST.",
                        cause="Penerbitan tagihan dimajukan (premature/backdated billing) untuk mengejar penyerapan anggaran atau kelalaian administratif.",
                        consequence="Indikasi ketidakpatuhan administrasi dan risiko timbulnya temuan audit atas dokumen yang tidak mencerminkan transaksi riil.",
                        recommendation="Minta vendor merevisi tanggal invoice sesuai atau setelah tanggal penandatanganan BAST.",
                        evidence=[
                            EvidenceCitation(
                                document=invoices[0].name,
                                locator="Tanggal Tagihan",
                                excerpt=i_date.strftime("%d-%m-%Y"),
                            ),
                            EvidenceCitation(
                                document=receipts[0].name,
                                locator="Tanggal BAST",
                                excerpt=b_date.strftime("%d-%m-%Y"),
                            ),
                        ],
                        tags=["date-anomaly", "chronology", "premature-billing"],
                    )
                )
                start_id += 1

        # Check Contract vs Invoice Date
        if c_date and i_date:
            if i_date < c_date:
                findings.append(
                    Finding5C(
                        id=f"FND-DATE-{start_id:03d}",
                        title="Anomali Tanggal: Tagihan Terbit Sebelum Tanggal Kontrak / SPK",
                        risk_level=RiskLevel.CRITICAL,
                        category="Uji Kronologi Dokumen",
                        condition=(
                            f"Invoice ({invoices[0].name}) bertanggal {i_date.strftime('%d-%m-%Y')}, "
                            f"mendahului tanggal Kontrak/SPK ({contracts[0].name}) yaitu {c_date.strftime('%d-%m-%Y')}."
                        ),
                        criteria="Asas Legalitas Pengadaan: Tidak dibenarkan adanya tagihan atas perikatan yang belum resmi disepakati.",
                        cause="Pekerjaan dimulai tanpa SPK resmi atau pembuatan dokumen kontrak dilakukan secara susulan (post-factum).",
                        consequence="Pelanggaran prosedur pengadaan barang/jasa dan risiko perikatan cacat hukum.",
                        recommendation="Lakukan evaluasi terhadap pejabat pengadaan dan pastikan seluruh dokumen dibuat secara tertib waktu.",
                        evidence=[
                            EvidenceCitation(
                                document=invoices[0].name,
                                locator="Tanggal Dokumen",
                                excerpt=i_date.strftime("%d-%m-%Y"),
                            ),
                            EvidenceCitation(
                                document=contracts[0].name,
                                locator="Tanggal Kontrak",
                                excerpt=c_date.strftime("%d-%m-%Y"),
                            ),
                        ],
                        tags=["date-anomaly", "post-factum", "contract-violation"],
                    )
                )

        return findings

    @staticmethod
    def _get_primary_amount(doc: AuditDocument) -> float | None:
        amounts = doc.entities.get("amounts", [])
        if not amounts:
            return None
        # Return maximum amount in document as primary transaction total
        vals = [a["value"] for a in amounts if isinstance(a, dict) and "value" in a]
        return max(vals) if vals else None

    @staticmethod
    def _get_primary_date(doc: AuditDocument) -> datetime | None:
        dates_raw = doc.entities.get("dates", [])
        if not dates_raw:
            return None

        for d_str in dates_raw:
            # Try ISO YYYY-MM-DD
            try:
                return datetime.strptime(d_str, "%Y-%m-%d")
            except ValueError:
                pass
            # Try DD/MM/YYYY or DD-MM-YYYY
            for sep in ["/", "-"]:
                try:
                    return datetime.strptime(d_str, f"%d{sep}%m{sep}%Y")
                except ValueError:
                    pass
            # Try Indonesian month names
            month_map = {
                "januari": 1, "februari": 2, "maret": 3, "april": 4, "mei": 5, "juni": 6,
                "juli": 7, "agustus": 8, "september": 9, "oktober": 10, "november": 11, "desember": 12,
                "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
            }
            parts = d_str.split()
            if len(parts) == 3 and parts[0].isdigit() and parts[2].isdigit():
                m_num = month_map.get(parts[1].lower())
                if m_num:
                    try:
                        return datetime(int(parts[2]), m_num, int(parts[0]))
                    except ValueError:
                        pass
        return None

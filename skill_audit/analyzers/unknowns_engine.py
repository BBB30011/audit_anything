"""Audit Inquiries and Unknowns Ledger engine (inspired by REA unknowns protocol).

In professional auditing, evidentiary gaps, missing records, and factual ambiguities
must not be guessed or hallucinated. Instead, they are registered into the
Unknowns Ledger as formal inquiries requiring management response or documentary proof.
"""

from __future__ import annotations

import re
from typing import Any

from skill_audit.models import AuditDocument, AuditDomain, Finding5C, UnknownItem, UnknownStatus


class UnknownsEngine:
    """Manages identification, tracking, and verification of audit unknowns and inquiries."""

    def analyze(
        self,
        documents: list[AuditDocument],
        findings: list[Finding5C],
        domain: AuditDomain | str = AuditDomain.GENERAL,
    ) -> list[UnknownItem]:
        """Scan documents and findings to automatically identify evidentiary gaps and open inquiries."""
        unknowns: list[UnknownItem] = []
        idx = 1

        doc_roles = [d.role_in_dossier.lower() for d in documents]
        doc_names = [d.name.lower() for d in documents]

        # 1. Missing Bank Payment Confirmation when Invoice exists
        has_invoice = any("invoice" in r for r in doc_roles)
        has_payment = any("payment" in r or "bukti_bayar" in r or "kuitansi" in r for r in doc_roles)
        if has_invoice and not has_payment:
            unknowns.append(
                UnknownItem(
                    id=f"UNK-{idx:02d}",
                    question="Apakah transaksi tagihan invoice pada berkas ini telah dilunasi melalui transfer kas/bank?",
                    category="Financial & Treasury",
                    status=UnknownStatus.OPEN,
                    impact="Ketidakpastian pengakuan kas keluar, risiko klaim denda penagihan ganda, atau kewajiban menggantung.",
                    evidence_required="Bukti Transfer Bank (Rekening Koran) atau Kuitansi Asli pelunasan dari vendor.",
                )
            )
            idx += 1

        # 2. Missing Goods Receipt / BAST when Contract exists
        has_contract = any("contract" in r or "spk" in r for r in doc_roles)
        has_bast = any("goods_receipt" in r or "bast" in r for r in doc_roles)
        if has_contract and not has_bast:
            unknowns.append(
                UnknownItem(
                    id=f"UNK-{idx:02d}",
                    question="Apakah seluruh ruang lingkup pekerjaan atau penyerahan barang telah diperiksa dan diterima secara fisik?",
                    category="Operational & Delivery",
                    status=UnknownStatus.OPEN,
                    impact="Pekerjaan belum tentu selesai atau barang belum tentu terkirim sesuai spesifikasi teknis SPK.",
                    evidence_required="Berita Acara Serah Terima (BAST), Surat Jalan (Surat Pengantar), atau Laporan Uji Fungsi.",
                )
            )
            idx += 1

        # 3. Missing Tax Settlement Proof (e-Faktur / SSP) when PPN/PPh is billed
        total_tax_mentioned = False
        for doc in documents:
            if any(k in doc.content.lower() for k in ["ppn", "pph", "faktur pajak"]):
                total_tax_mentioned = True
                break

        has_tax_doc = any("tax" in r or "faktur_pajak" in r or "ssp" in r for r in doc_roles)
        if total_tax_mentioned and not has_tax_doc:
            unknowns.append(
                UnknownItem(
                    id=f"UNK-{idx:02d}",
                    question="Apakah pemotongan/pemungutan PPN dan PPh atas tagihan ini telah disetor ke kas negara dan dilaporkan melalui e-Faktur/SPT Masa?",
                    category="Tax Compliance",
                    status=UnknownStatus.OPEN,
                    impact="Risiko sanksi denda administrasi perpajakan dan ketidakabsahan pengkreditan Pajak Masukan.",
                    evidence_required="Faktur Pajak Elektronik (e-Faktur valid QR DJP) dan Bukti Penerimaan Negara (BPN / NTPN).",
                )
            )
            idx += 1

        # 4. Domain-Adaptive Evidentiary Checks
        domain_str = domain.value if isinstance(domain, AuditDomain) else str(domain).lower()
        full_corpus = " ".join(d.content.lower() for d in documents)

        if domain_str == "healthcare" or any(k in full_corpus for k in ["pasien", "rawat inap", "rsud", "klaim bpjs"]):
            has_resume = any("resume" in d.name.lower() or "discharge" in d.name.lower() for d in documents)
            if not has_resume:
                unknowns.append(
                    UnknownItem(
                        id=f"UNK-{idx:02d}",
                        question="Apakah tindakan medis dan diagnosa pasien didukung Resume Medis (Discharge Summary) resmi DPJP?",
                        category="Healthcare Clinical Proof",
                        status=UnknownStatus.OPEN,
                        impact="Potensi penolakan klaim BPJS/Asuransi atau indikasi upcoding tindakan tanpa persetujuan dokter.",
                        evidence_required="Resume Medis Pasien yang ditandatangani Dokter Penanggung Jawab Pelayanan (DPJP).",
                    )
                )
                idx += 1

        if domain_str == "government" or any(k in full_corpus for k in ["apbn", "apbd", "dpa", "sp2d"]):
            has_sp2d = any("sp2d" in d.name.lower() or "spm" in d.name.lower() for d in documents)
            if not has_sp2d:
                unknowns.append(
                    UnknownItem(
                        id=f"UNK-{idx:02d}",
                        question="Apakah realisasi pembayaran beban anggaran telah diterbitkan Surat Perintah Pencairan Dana (SP2D)?",
                        category="Public Sector Treasury",
                        status=UnknownStatus.OPEN,
                        impact="Ketidakpastian beban kas daerah/negara dan potensi temuan kepatuhan BPK atas belanja tanpa SP2D.",
                        evidence_required="Lembar Asli SP2D bertandatangan Kuasa BUD dan SPM terverifikasi.",
                    )
                )
                idx += 1

        if domain_str == "hr_payroll" or any(k in full_corpus for k in ["payroll", "lembur", "slip gaji"]):
            has_bpjs = any("bpjs" in d.name.lower() or "1721" in d.name.lower() for d in documents)
            if not has_bpjs:
                unknowns.append(
                    UnknownItem(
                        id=f"UNK-{idx:02d}",
                        question="Apakah kewajiban iuran BPJS Ketenagakerjaan/Kesehatan dan pelaporan SPT PPh 21 telah disetor?",
                        category="HR Statutory Compliance",
                        status=UnknownStatus.OPEN,
                        impact="Pelanggaran UU Ketenagakerjaan, denda administratif, dan hak jaminan sosial karyawan terabaikan.",
                        evidence_required="Bukti Bayar Iuran BPJS Ketenagakerjaan & Bukti Penerimaan Elektronik (BPE) SPT PPh 21.",
                    )
                )
                idx += 1

        if domain_str == "supply_chain" or any(k in full_corpus for k in ["stock opname", "gudang", "inventory"]):
            has_baso = any("baso" in d.name.lower() or "opname" in d.name.lower() for d in documents)
            if not has_baso:
                unknowns.append(
                    UnknownItem(
                        id=f"UNK-{idx:02d}",
                        question="Apakah saldo stok sistem telah diverifikasi melalui Berita Acara Stock Opname (BASO) fisik?",
                        category="Supply Chain & Physical Custody",
                        status=UnknownStatus.OPEN,
                        impact="Risiko kehilangan persediaan (inventory shrinkage), dead-stock tidak teridentifikasi, dan selisih neraca.",
                        evidence_required="Berita Acara Stock Opname (BASO) fisik bertandatangan tim penghitung independen.",
                    )
                )
                idx += 1

        # 5. Unknowns derived from unresolved 5C findings
        for f in findings:
            if "fiktif" in f.cause.lower() or "anomali" in f.title.lower() or "kronologi" in f.title.lower():
                unknowns.append(
                    UnknownItem(
                        id=f"UNK-{idx:02d}",
                        question=f"Klarifikasi Manajemen: Bagaimana penjelasan resmi terkait {f.title}?",
                        category="Audit Finding Inquiry",
                        status=UnknownStatus.OPEN,
                        impact=f"Dampak signifikan terhadap opini audit: {f.consequence[:120]}...",
                        evidence_required="Surat Klarifikasi Tertulis dari Pejabat Pembuat Komitmen (PPK) atau Manager terkait.",
                        evidence_ref=f.id,
                    )
                )
                idx += 1

        return unknowns

    @staticmethod
    def resolve_unknown(
        unknown: UnknownItem,
        notes: str,
        resolved_by: str = "Human Auditor",
        evidence_ref: str = "",
    ) -> UnknownItem:
        """Resolve an open unknown by providing substantiating notes and evidence references."""
        unknown.status = UnknownStatus.RESOLVED
        unknown.resolution_notes = notes
        unknown.resolved_by = resolved_by
        unknown.evidence_ref = evidence_ref
        return unknown

    @staticmethod
    def waive_unknown(
        unknown: UnknownItem,
        rationale: str,
        waived_by: str = "Lead Auditor",
    ) -> UnknownItem:
        """Formally waive an unknown with explicit auditor rationale (accepted audit risk)."""
        unknown.status = UnknownStatus.WAIVED
        unknown.resolution_notes = f"[WAIVED / DILEPAS]: {rationale}"
        unknown.resolved_by = waived_by
        return unknown

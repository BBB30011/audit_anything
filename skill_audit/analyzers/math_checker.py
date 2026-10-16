"""Substantive and arithmetic analyzer for financial numbers, taxes, and tables."""

from __future__ import annotations

import re

from skill_audit.grounding import normalize_evidence
from skill_audit.models import (
    AuditDocument,
    EvidenceCitation,
    Finding5C,
    RiskLevel,
)


class MathChecker:
    """Analyzes mathematical consistency in financial documents: line totals, tax, and sum checks."""

    def analyze(self, documents: list[AuditDocument]) -> list[Finding5C]:
        findings: list[Finding5C] = []
        finding_counter = 1

        for doc in documents:
            # Check line-by-line calculations (e.g., Qty * Price = Total)
            line_findings = self._check_multiplications(doc, start_id=finding_counter)
            findings.extend(line_findings)
            finding_counter += len(line_findings)

            # Check tax calculations (e.g., PPN 11% or 10%)
            tax_findings = self._check_tax_calculations(doc, start_id=finding_counter)
            findings.extend(tax_findings)
            finding_counter += len(tax_findings)

        return findings

    def _check_multiplications(self, doc: AuditDocument, start_id: int) -> list[Finding5C]:
        findings: list[Finding5C] = []
        # Pattern e.g.: "10 x 50.000 = 550.000" or "Qty: 10 | Harga: 50.000 | Total: 550.000"
        mult_patterns = [
            r"(\d+)\s*(?:x|\*)\s*(?:Rp\.?|IDR)?\s*([0-9\.\,]+)\s*(?:=|\:)\s*(?:Rp\.?|IDR)?\s*([0-9\.\,]+)",
            r"(?:Qty|Kuantitas)[:\s]*(\d+)[^0-9\n\r]*(?:Harga|Tarif)[:\s]*(?:Rp\.?|IDR)?\s*([0-9\.\,]+)[^0-9\n\r]*(?:Total|Jumlah)[:\s]*(?:Rp\.?|IDR)?\s*([0-9\.\,]+)",
        ]

        for pattern in mult_patterns:
            for match in re.finditer(pattern, doc.content, flags=re.IGNORECASE):
                try:
                    qty = float(match.group(1))
                    price = self._parse_num(match.group(2))
                    total_stated = self._parse_num(match.group(3))

                    expected_total = qty * price
                    # Check if discrepancy is greater than 1.0 (to avoid tiny float issues)
                    if abs(expected_total - total_stated) > 1.0:
                        quote = normalize_evidence(match.group(0))
                        diff = total_stated - expected_total
                        finding = Finding5C(
                            id=f"FND-MATH-{start_id:03d}",
                            title=f"Selisih Perhitungan Aritmatika pada {doc.name}",
                            risk_level=RiskLevel.HIGH if abs(diff) > 500000 else RiskLevel.MEDIUM,
                            category="Uji Aritmatika & Perhitungan",
                            condition=(
                                f"Ditemukan kesalahan perkalian kuantitas dan harga satuan: "
                                f"{qty:g} x Rp {price:,.0f} tercatat Rp {total_stated:,.0f}, "
                                f"seharusnya Rp {expected_total:,.0f}. Terdapat selisih sebesar Rp {abs(diff):,.0f}."
                            ),
                            criteria="Standar Akuntansi Keuangan (SAK) dan Ketentuan Klausul Pembayaran Kontrak (akurasi nilai tagihan).",
                            cause="Ketidaktelitian dalam penyusunan rincian tagihan atau kesalahan input matematis tanpa validasi otomatis.",
                            consequence=(
                                f"Potensi {'kelebihan pembayaran (overpayment)' if diff > 0 else 'kurang bayar (underpayment)'} "
                                f"senilai Rp {abs(diff):,.0f} yang dapat membebani anggaran dan menjadi temuan audit kepatuhan."
                            ),
                            recommendation="Lakukan konfirmasi kepada penyedia/vendor dan terbitkan Nota Koreksi (Credit/Debit Note) untuk menyesuaikan nilai tagihan riil.",
                            evidence=[
                                EvidenceCitation(
                                    document=doc.name,
                                    locator="Teks Transaksi",
                                    excerpt=quote,
                                )
                            ],
                            tags=["arithmetic", "calculation-error", "math"],
                        )
                        findings.append(finding)
                        start_id += 1
                except Exception:
                    continue

        return findings

    def _check_tax_calculations(self, doc: AuditDocument, start_id: int) -> list[Finding5C]:
        findings: list[Finding5C] = []
        # Pattern for Subtotal and PPN (e.g. Subtotal: 100.000.000, PPN: 12.000.000 instead of 11% = 11.000.000)
        tax_pattern = r"(?:Subtotal|DPP|Dasar Pengenaan Pajak)[:\s]*(?:Rp\.?|IDR)?\s*([0-9\.\,]+)[\s\S]{1,150}?(?:PPN|Pajak Pertambahan Nilai)(?:\s*(?:11%|10%))?[:\s]*(?:Rp\.?|IDR)?\s*([0-9\.\,]+)"

        for match in re.finditer(tax_pattern, doc.content, flags=re.IGNORECASE):
            try:
                dpp = self._parse_num(match.group(1))
                ppn_stated = self._parse_num(match.group(2))

                if dpp <= 0:
                    continue

                # Standard Indonesian VAT (PPN) is 11% (UU HPP No. 7 Tahun 2021)
                expected_ppn_11 = dpp * 0.11
                expected_ppn_10 = dpp * 0.10

                # Check if matches neither 11% nor 10% (within tolerance of 100 Rupiah for rounding)
                if abs(ppn_stated - expected_ppn_11) > 100 and abs(ppn_stated - expected_ppn_10) > 100:
                    quote = normalize_evidence(match.group(0)[:200])
                    diff = ppn_stated - expected_ppn_11
                    finding = Finding5C(
                        id=f"FND-TAX-{start_id:03d}",
                        title=f"Ketidaksesuaian Perhitungan PPN pada {doc.name}",
                        risk_level=RiskLevel.HIGH,
                        category="Aritmatika & Perhitungan Pajak",
                        condition=(
                            f"Perhitungan PPN atas DPP senilai Rp {dpp:,.0f} tercantum Rp {ppn_stated:,.0f}. "
                            f"Berdasarkan tarif PPN 11%, nilai PPN yang benar adalah Rp {expected_ppn_11:,.0f}."
                        ),
                        criteria="UU Nomor 7 Tahun 2021 tentang Harmonisasi Peraturan Perpajakan (UU HPP) Pasal 7 (Tarif PPN 11%).",
                        cause="Kesalahan penerapan formula pajak atau perhitungan manual yang tidak sesuai regulasi perpajakan yang berlaku.",
                        consequence="Risiko sanksi denda administrasi perpajakan atau penolakan kredit faktur pajak oleh DJP.",
                        recommendation="Revisi faktur pajak dan invoice dengan perhitungan PPN 11% yang benar serta koordinasikan dengan bagian perpajakan.",
                        evidence=[
                            EvidenceCitation(
                                document=doc.name,
                                locator="Rincian Pajak",
                                excerpt=quote,
                            )
                        ],
                        tags=["tax", "ppn", "compliance"],
                    )
                    findings.append(finding)
                    start_id += 1
            except Exception:
                continue

        return findings

    @staticmethod
    def _parse_num(val_str: str) -> float:
        cleaned = val_str.strip()
        if "." in cleaned and "," in cleaned:
            # Indonesian format 1.000.000,00
            if cleaned.rfind(",") > cleaned.rfind("."):
                cleaned = cleaned.replace(".", "").replace(",", ".")
            else:  # US format 1,000,000.00
                cleaned = cleaned.replace(",", "")
        elif "." in cleaned:
            parts = cleaned.split(".")
            # If parts after dot has 3 digits, it's a thousand separator
            if all(len(p) == 3 for p in parts[1:]):
                cleaned = "".join(parts)
            else:
                pass  # standard float
        elif "," in cleaned:
            parts = cleaned.split(",")
            if all(len(p) == 3 for p in parts[1:]):
                cleaned = "".join(parts)
            else:
                cleaned = cleaned.replace(",", ".")
        return float(cleaned)

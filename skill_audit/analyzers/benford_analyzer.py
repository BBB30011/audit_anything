"""Forensic Benford's Law Digital Analysis Engine.

Implements Nigrini (2012) first-digit and mathematical distribution testing
to detect data manipulation, fabricated invoices, and creative accounting.
"""

from __future__ import annotations

import math
import re
from typing import Any

from skill_audit.models import (
    AuditDocument,
    BenfordAnalysisResult,
    BenfordDigitStat,
    EvidenceCitation,
    Finding5C,
    RiskLevel,
    RiskScore5x5,
)

# Standard Benford's Law expected probabilities for first digits 1..9
BENFORD_EXPECTED_FIRST_DIGIT: dict[int, float] = {
    d: math.log10(1.0 + 1.0 / d) for d in range(1, 10)
}


class BenfordForensicAnalyzer:
    """Forensic analyzer evaluating digit distributions across numeric transactions."""

    def __init__(self, min_sample_size: int = 15) -> None:
        self.min_sample_size = min_sample_size

    def analyze(
        self, documents: list[AuditDocument]
    ) -> tuple[BenfordAnalysisResult, list[Finding5C]]:
        """Extract numbers across all documents and evaluate Benford's Law conformity."""
        numbers: list[float] = []
        doc_sources: dict[float, str] = {}

        for doc in documents:
            extracted = self._extract_numbers(doc)
            for n in extracted:
                numbers.append(n)
                if n not in doc_sources:
                    doc_sources[n] = doc.name

        total_numbers = len(numbers)
        if total_numbers == 0:
            return (
                BenfordAnalysisResult(
                    total_numbers=0,
                    analyzed_digits=0,
                    conformity_status="no_numeric_data",
                ),
                [],
            )

        # Count first digits 1..9
        first_digit_counts: dict[int, int] = {d: 0 for d in range(1, 10)}
        analyzed_count = 0

        for num in numbers:
            d = self._get_first_digit(num)
            if d in first_digit_counts:
                first_digit_counts[d] += 1
                analyzed_count += 1

        if analyzed_count == 0:
            return (
                BenfordAnalysisResult(
                    total_numbers=total_numbers,
                    analyzed_digits=0,
                    conformity_status="insufficient_data",
                ),
                [],
            )

        # Calculate statistics per digit
        digit_stats: list[BenfordDigitStat] = []
        mad_sum = 0.0
        chi_square = 0.0
        critical_anomalies: list[int] = []

        for d in range(1, 10):
            count = first_digit_counts[d]
            actual_pct = (count / analyzed_count) * 100.0
            expected_pct = BENFORD_EXPECTED_FIRST_DIGIT[d] * 100.0
            diff_pct = actual_pct - expected_pct

            # Absolute difference for MAD
            diff_ratio = abs((count / analyzed_count) - BENFORD_EXPECTED_FIRST_DIGIT[d])
            mad_sum += diff_ratio

            # Chi-square contribution: (O - E)^2 / E
            expected_count = analyzed_count * BENFORD_EXPECTED_FIRST_DIGIT[d]
            if expected_count > 0:
                chi_square += ((count - expected_count) ** 2) / expected_count

            # Z-score calculation
            p = BENFORD_EXPECTED_FIRST_DIGIT[d]
            variance = (p * (1.0 - p)) / analyzed_count
            std_dev = math.sqrt(variance) if variance > 0 else 1.0
            z_score = ((count / analyzed_count) - p) / std_dev if std_dev > 0 else 0.0

            # Significant deviation flag (|Z| > 2.58 is 99% confidence level)
            if abs(z_score) > 2.58 and analyzed_count >= self.min_sample_size:
                critical_anomalies.append(d)

            digit_stats.append(
                BenfordDigitStat(
                    digit=d,
                    actual_count=count,
                    actual_pct=actual_pct,
                    expected_pct=expected_pct,
                    diff_pct=diff_pct,
                    z_score=z_score,
                )
            )

        mad = mad_sum / 9.0

        # Nigrini (2012) first-digit conformity thresholds
        if analyzed_count < self.min_sample_size:
            conformity_status = "acceptable (small sample)"
        elif mad <= 0.006:
            conformity_status = "close_conformity"
        elif mad <= 0.012:
            conformity_status = "acceptable_conformity"
        elif mad <= 0.015:
            conformity_status = "marginally_acceptable"
        else:
            conformity_status = "non_conforming"

        result = BenfordAnalysisResult(
            total_numbers=total_numbers,
            analyzed_digits=analyzed_count,
            conformity_status=conformity_status,
            mad_score=mad,
            chi_square=chi_square,
            critical_anomalies=critical_anomalies,
            digit_distribution=digit_stats,
        )

        findings: list[Finding5C] = []
        if conformity_status == "non_conforming" and analyzed_count >= self.min_sample_size:
            anom_str = ", ".join(f"Digit {d}" for d in critical_anomalies) or "sebaran merata non-alami"
            finding = Finding5C(
                id="FND-BNF-001",
                title=f"Anomali Distribusi Forensik Angka Transaksi (Penyimpangan Benford's Law: {anom_str})",
                risk_level=RiskLevel.HIGH,
                category="Forensik & Integritas Transaksi",
                condition=(
                    f"Distribusi digit pertama dari {analyzed_count} angka transaksi menunjukkan penyimpangan "
                    f"signifikan dari hukum distribusi alami Benford's Law. Skor MAD tercatat {mad:.4f} "
                    f"(ambang batas normal <= 0.012) dengan status 'non_conforming'. "
                    f"Lonjakan anomali terdeteksi pada {anom_str}."
                ),
                criteria=(
                    "Standar Akuntansi Forensik & Pengujian Digital (Nigrini Digital Analysis, "
                    "ISA 240 / SA 240 Tanggung Jawab Auditor Terkait Kecurangan)."
                ),
                cause=(
                    "Indikasi manipulasi angka (human number fabrication bias), pemecahan transaksi artifisial, "
                    "atau penyusunan faktur/bukti pengeluaran yang tidak bersumber dari transaksi riil pasar."
                ),
                consequence=(
                    "Potensi transaksi fiktif, markup anggaran, atau penghindaran batas persetujuan berwenang "
                    "yang dapat menimbulkan kerugian material pada entitas."
                ),
                recommendation=(
                    f"Lakukan pengujian substantif mendalam (100% substantive test) terhadap seluruh transaksi "
                    f"yang dimulai dengan digit anomali ({anom_str}) serta mintakan konfirmasi pihak ketiga independen."
                ),
                evidence=[
                    EvidenceCitation(
                        document="Analisis Forensik Benford",
                        locator=f"MAD: {mad:.4f}, Chi-Square: {chi_square:.2f}",
                        excerpt=f"Total sampel: {analyzed_count} angka. Anomali kritis: {anom_str}",
                    )
                ],
                tags=["benford", "forensic", "fraud", "digital-analysis"],
                risk_score=RiskScore5x5(likelihood=4, impact=4),
                coso_component="Aktivitas Pengendalian (Control Activities)",
                business_process="Forensic Analysis",
            )
            findings.append(finding)

        return result, findings

    def _extract_numbers(self, doc: AuditDocument) -> list[float]:
        """Extract meaningful transaction amounts and numerical figures from an AuditDocument."""
        numbers: list[float] = []

        # 1. From pre-extracted entities if available
        amounts = doc.entities.get("amounts", [])
        if amounts:
            for a in amounts:
                if isinstance(a, dict) and "value" in a:
                    v = float(a["value"])
                    if v >= 10.0:
                        numbers.append(v)
                elif isinstance(a, (int, float)):
                    v = float(a)
                    if v >= 10.0:
                        numbers.append(v)
            return numbers

        # 2. Fallback to document content regex if entities are absent
        matches = re.findall(r"(?:Rp\.?|IDR|\$)?\s*([1-9]\d{2,}(?:[.,]\d+)*)", doc.content)
        for m in matches:
            cleaned = m.replace(".", "").replace(",", "")
            # filter out common 4-digit years (1980 - 2035)
            if len(cleaned) == 4 and 1980 <= int(cleaned) <= 2035:
                continue
            # filter out phone numbers or postal codes
            if len(cleaned) >= 10 and (cleaned.startswith("08") or cleaned.startswith("62")):
                continue
            try:
                val = float(cleaned)
                if val >= 10.0:
                    numbers.append(val)
            except ValueError:
                continue

        return numbers

    @staticmethod
    def _get_first_digit(number: float) -> int:
        """Extract the leading non-zero digit."""
        s = f"{abs(number):.6f}".lstrip("0").replace(".", "")
        if s:
            return int(s[0])
        return 0

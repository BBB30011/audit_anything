"""Governance, Risk, and Compliance (GRC) knowledge base and rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AuthorityThreshold:
    role_level: str
    max_amount_opex: float
    max_amount_capex: float
    requires_dual_signature: bool
    description: str


# Standard Corporate Delegation of Authority (DoA) Matrix
DEFAULT_DOA_MATRIX: list[AuthorityThreshold] = [
    AuthorityThreshold(
        role_level="Staff / Supervisor",
        max_amount_opex=10_000_000.0,
        max_amount_capex=0.0,
        requires_dual_signature=False,
        description="Pengeluaran operasional rutin bernilai kecil (petty cash / ATK).",
    ),
    AuthorityThreshold(
        role_level="Department Manager",
        max_amount_opex=100_000_000.0,
        max_amount_capex=50_000_000.0,
        requires_dual_signature=True,
        description="Belanja departemen yang telah dianggarkan dalam RKAP tahunan.",
    ),
    AuthorityThreshold(
        role_level="General Manager / Vice President",
        max_amount_opex=500_000_000.0,
        max_amount_capex=250_000_000.0,
        requires_dual_signature=True,
        description="Pengadaan barang/jasa bernilai menengah dan kontrak tahunan.",
    ),
    AuthorityThreshold(
        role_level="Direktur Keuangan / Direktur Operasional",
        max_amount_opex=2_500_000_000.0,
        max_amount_capex=1_000_000_000.0,
        requires_dual_signature=True,
        description="Perikatan strategis dan komitmen belanja tingkat korporasi.",
    ),
    AuthorityThreshold(
        role_level="Direktur Utama (CEO)",
        max_amount_opex=10_000_000_000.0,
        max_amount_capex=5_000_000_000.0,
        requires_dual_signature=True,
        description="Pengadaan skala besar di tingkat Dewan Direksi.",
    ),
    AuthorityThreshold(
        role_level="Dewan Komisaris / RUPS",
        max_amount_opex=float("inf"),
        max_amount_capex=float("inf"),
        requires_dual_signature=True,
        description="Transaksi material (> 20% ekuitas / melebihi ambang batas kewenangan Direksi).",
    ),
]


GCG_PRINCIPLES = {
    "transparency": {
        "title": "Transparansi (Transparency)",
        "definition": "Keterbukaan dalam melaksanakan proses pengambilan keputusan dan keterbukaan dalam mengungkapkan informasi material dan relevan mengenai perusahaan.",
        "audit_checks": [
            "Ketersediaan laporan berkala kepada stakeholder",
            "Publikasi pengumuman lelang dan pengadaan secara terbuka",
            "Keterbukaan informasi harga dan spesifikasi teknis",
        ],
    },
    "accountability": {
        "title": "Akuntabilitas (Accountability)",
        "definition": "Kejelasan fungsi, pelaksanaan, dan pertanggungjawaban organ perusahaan sehingga pengelolaan berjalan secara efektif.",
        "audit_checks": [
            "Pemisahan tugas yang tegas (Segregation of Duties)",
            "Kepatuhan terhadap batas kewenangan otorisasi (Delegation of Authority)",
            "Audit trail transaksi yang tidak dapat dimanipulasi",
        ],
    },
    "responsibility": {
        "title": "Responsibilitas (Responsibility)",
        "definition": "Kesesuaian pengelolaan perusahaan terhadap peraturan perundang-undangan dan prinsip korporasi yang sehat.",
        "audit_checks": [
            "Kepatuhan pelaporan pajak (PPh & PPN)",
            "Pemenuhan ketentuan ketenagakerjaan dan jaminan sosial",
            "Kepatuhan regulasi lingkungan hidup dan keselamatan kerja",
        ],
    },
    "independency": {
        "title": "Independensi (Independency)",
        "definition": "Keadaan di mana perusahaan dikelola secara profesional tanpa benturan kepentingan dan pengaruh/tekanan dari pihak mana pun yang tidak sesuai perundang-undangan.",
        "audit_checks": [
            "Pernyataan bebas benturan kepentingan (Conflict of Interest Disclosure)",
            "Uji kepatutan dan kelayakan (Due Diligence) rekanan",
            "Larangan perangkapan jabatan terlarang",
        ],
    },
    "fairness": {
        "title": "Kewajaran & Kesetaraan (Fairness)",
        "definition": "Keadilan dan kesetaraan dalam memenuhi hak-hak pemangku kepentingan yang timbul berdasarkan perjanjian dan peraturan perundang-undangan.",
        "audit_checks": [
            "Perlakuan setara kepada seluruh peserta tender pengadaan",
            "Pembayaran tagihan vendor tepat waktu sesuai kontrak",
            "Penyelesaian perselisihan yang objektif dan adil",
        ],
    },
}


def evaluate_doa_limit(amount: float, approver_title: str) -> tuple[bool, float, str]:
    """Check if transaction amount exceeds approver's maximum threshold.

    Returns (is_compliant, authorized_limit, message).
    """
    title_lower = approver_title.lower()
    matched_threshold: AuthorityThreshold | None = None

    if any(k in title_lower for k in ["komisaris", "rups", "board of commissioners"]):
        matched_threshold = DEFAULT_DOA_MATRIX[5]
    elif any(k in title_lower for k in ["direktur utama", "ceo", "president director"]):
        matched_threshold = DEFAULT_DOA_MATRIX[4]
    elif any(k in title_lower for k in ["direktur", "director", "cfo", "coo", "cto"]):
        matched_threshold = DEFAULT_DOA_MATRIX[3]
    elif any(k in title_lower for k in ["general manager", "vp", "vice president", "kepala divisi"]):
        matched_threshold = DEFAULT_DOA_MATRIX[2]
    elif any(k in title_lower for k in ["manager", "manajer", "kepala bagian", "ppk"]):
        matched_threshold = DEFAULT_DOA_MATRIX[1]
    else:
        matched_threshold = DEFAULT_DOA_MATRIX[0]

    limit = matched_threshold.max_amount_opex
    if amount > limit:
        return (
            False,
            limit,
            f"Nilai transaksi Rp {amount:,.0f} melampaui batas kewenangan {matched_threshold.role_level} (Maksimum Rp {limit:,.0f}).",
        )
    return True, limit, "Nilai transaksi dalam batas kewenangan yang sah."

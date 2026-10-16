"""Technical IT, ITGC, and Digital Audit knowledge base."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ITGCControlDomain:
    domain_code: str
    name: str
    description: str
    control_objectives: list[str]


ITGC_DOMAINS: list[ITGCControlDomain] = [
    ITGCControlDomain(
        domain_code="ITGC-AC",
        name="Access to Programs and Data (Akses Program & Data)",
        description="Memastikan hanya pengguna terotorisasi yang memiliki akses ke sistem keuangan, aplikasi bisnis, dan basis data.",
        control_objectives=[
            "Penerapan otentikasi multi-faktor (MFA) pada seluruh akses jarak jauh dan akun administrator.",
            "Penonaktifan akun pegawai non-aktif (terminasi/resign) maksimal 1x24 jam.",
            "Review berkala hak akses istimewa (Privileged Access / Superuser) minimal tiap kuartal.",
            "Pemisahan tugas (SoD) terkonfigurasi di tingkat role-based access control (RBAC).",
        ],
    ),
    ITGCControlDomain(
        domain_code="ITGC-CH",
        name="Program Changes (Manajemen Perubahan Program)",
        description="Memastikan modifikasi sistem, patch, dan konfigurasi telah diuji, disetujui, dan diterapkan secara terkontrol.",
        control_objectives=[
            "Setiap perubahan kode memiliki tiket Change Request (CR) dan persetujuan Change Advisory Board (CAB).",
            "Pemisahan lingkungan kerja yang tegas antara Development, Staging (UAT), dan Production.",
            "Pengembang aplikasi tidak memiliki akses tulis (write/execute) langsung ke server produksi.",
            "Ketersediaan rencana pembatalan (Backout / Rollback Plan) sebelum deployment rilis.",
        ],
    ),
    ITGCControlDomain(
        domain_code="ITGC-CO",
        name="Computer Operations (Operasional Komputer & Backup)",
        description="Memastikan kesinambungan operasional, pemrosesan batch data terjadwal, dan pencadangan data yang andal.",
        control_objectives=[
            "Pencadangan data (backup) harian otomatis terenkripsi dan disimpan di lokasi terpisah (off-site / cloud).",
            "Uji pemulihan cadangan data (Restore Drill) berkala minimal 2 kali setahun.",
            "Pemantauan kegagalan batch job keuangan (Batch Processing Monitoring) dan notifikasi otomatis.",
            "Sinkronisasi waktu sistem menggunakan Network Time Protocol (NTP) terpusat.",
        ],
    ),
    ITGCControlDomain(
        domain_code="ITGC-PD",
        name="Program Development (Pengembangan Sistem Baru)",
        description="Memastikan metodologi pengembangan sistem mengintegrasikan analisis risiko keamanan dan pengujian menyeluruh.",
        control_objectives=[
            "Penerapan Secure Software Development Life Cycle (SSDLC).",
            "Pengujian penetrasi keamanan (Penetration Testing) dan pemindaian kerentanan (SAST/DAST) sebelum go-live.",
            "Persetujuan resmi kesiapan operasional (User Acceptance Testing - UAT sign-off).",
        ],
    ),
]


def compute_file_sha256(file_path: Path | str) -> str:
    """Calculate SHA-256 cryptographic digest of a file to verify evidence integrity."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_audit_trail_integrity(log_lines: list[str]) -> tuple[bool, list[str]]:
    """Verify continuity of timestamps and sequential event sequencing in log files."""
    issues: list[str] = []
    timestamp_pattern = re.compile(r"(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2})")

    prev_time = None
    for idx, line in enumerate(log_lines, 1):
        match = timestamp_pattern.search(line)
        if match:
            t_str = match.group(1)
            if prev_time and t_str < prev_time:
                issues.append(f"Baris {idx}: Anomali urutan waktu terdeteksi ({t_str} mendahului {prev_time}). Kemungkinan rekayasa log.")
            prev_time = t_str

    return len(issues) == 0, issues

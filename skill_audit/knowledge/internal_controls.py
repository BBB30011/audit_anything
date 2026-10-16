"""COSO Internal Control framework and Segregation of Duties (SoD) knowledge base."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class COSOPrinciple:
    component: str
    principle_no: int
    title: str
    description: str


COSO_17_PRINCIPLES: list[COSOPrinciple] = [
    # 1. Control Environment
    COSOPrinciple("Control Environment", 1, "Komitmen terhadap Integritas dan Nilai Etika", "Organisasi menunjukkan komitmen kuat terhadap integritas dan nilai-nilai etika luhur."),
    COSOPrinciple("Control Environment", 2, "Independensi Dewan Pengawas", "Dewan Komisaris menunjukkan independensi dari manajemen dan mengawasi pengendalian internal."),
    COSOPrinciple("Control Environment", 3, "Struktur dan Garis Pelaporan", "Manajemen menetapkan struktur organisasi, garis pelaporan, wewenang, dan tanggung jawab."),
    COSOPrinciple("Control Environment", 4, "Kompetensi Sumber Daya Manusia", "Komitmen untuk merekrut, mengembangkan, dan mempertahankan individu yang kompeten."),
    COSOPrinciple("Control Environment", 5, "Penegakan Akuntabilitas", "Menegakkan akuntabilitas individu atas tanggung jawab pengendalian internal."),
    # 2. Risk Assessment
    COSOPrinciple("Risk Assessment", 6, "Spesifikasi Tujuan yang Jelas", "Menetapkan tujuan organisasi yang terukur untuk memungkinkan identifikasi risiko."),
    COSOPrinciple("Risk Assessment", 7, "Identifikasi & Analisis Risiko", "Mengidentifikasi risiko pencapaian tujuan di seluruh entitas dan menganalisis dampaknya."),
    COSOPrinciple("Risk Assessment", 8, "Penilaian Potensi Kecurangan (Fraud Risk)", "Mempertimbangkan potensi kecurangan dalam menilai risiko entitas."),
    COSOPrinciple("Risk Assessment", 9, "Identifikasi Perubahan Signifikan", "Mengidentifikasi dan menilai perubahan internal/eksternal yang dapat berdampak pada pengendalian."),
    # 3. Control Activities
    COSOPrinciple("Control Activities", 10, "Pemilihan & Pengembangan Kontrol", "Memilih dan mengembangkan aktivitas pengendalian yang memitigasi risiko hingga tingkat yang dapat diterima."),
    COSOPrinciple("Control Activities", 11, "Kontrol Umum Teknologi Informasi (ITGC)", "Memilih dan mengembangkan kontrol umum atas teknologi untuk mendukung pencapaian tujuan."),
    COSOPrinciple("Control Activities", 12, "Implementasi Kebijakan & Prosedur", "Menerapkan aktivitas pengendalian melalui kebijakan tertulis dan prosedur operasional baku (SOP)."),
    # 4. Information & Communication
    COSOPrinciple("Information & Communication", 13, "Pemanfaatan Informasi Relevan", "Memperoleh atau menghasilkan dan menggunakan informasi relevan dan berkualitas."),
    COSOPrinciple("Information & Communication", 14, "Komunikasi Internal yang Efektif", "Mengomunikasikan informasi pengendalian internal secara internal ke seluruh unit."),
    COSOPrinciple("Information & Communication", 15, "Komunikasi Eksternal", "Berkomunikasi dengan pihak eksternal terkait hal-hal yang memengaruhi pengendalian internal."),
    # 5. Monitoring Activities
    COSOPrinciple("Monitoring Activities", 16, "Evaluasi Berkelanjutan & Terpisah", "Melakukan evaluasi berkala/mandiri (audit internal) untuk memastikan komponen pengendalian berfungsi."),
    COSOPrinciple("Monitoring Activities", 17, "Evaluasi & Komunikasi Defisiensi", "Mengevaluasi dan mengomunikasikan defisiensi pengendalian tepat waktu kepada pihak penanggung jawab."),
]


# Segregation of Duties (SoD) Conflict Rules
SOD_RULES = [
    {
        "code": "SOD-01",
        "title": "Pemesanan vs Penerimaan Barang (Purchasing vs Receiving)",
        "role_a_keywords": ["pejabat pengadaan", "purchasing", "buyer", "panitia pengadaan"],
        "role_b_keywords": ["tim penerima", "gudang", "receiving", "pemeriksa barang", "bast"],
        "risk_explanation": "Jika staf pembuat pesanan juga menandatangani penerimaan barang, timbul risiko barang fiktif dilaporkan seolah telah diterima.",
        "recommendation": "Pisahkan secara tegas panitia pengadaan dengan tim pemeriksa penerimaan hasil pekerjaan (PPHP/BAST).",
    },
    {
        "code": "SOD-02",
        "title": "Pembuat Komitmen (Inisiator) vs Penyetuju Pembayaran (Approver)",
        "role_a_keywords": ["pembuat komitmen", "inisiator", "staff pengadaan", "pemohon dana"],
        "role_b_keywords": ["penyetuju", "approver", "manager keuangan", "cfo", "otorisator"],
        "risk_explanation": "Self-approval: seseorang menyetujui pembayarannya sendiri tanpa pengawasan independen.",
        "recommendation": "Terapkan prinsip Maker-Checker-Signer independen pada setiap tahapan pengeluaran kas.",
    },
    {
        "code": "SOD-03",
        "title": "Pemelihara Master Vendor vs Pembuat Invoice / Pembayaran",
        "role_a_keywords": ["master vendor", "registrasi vendor", "vendor admin"],
        "role_b_keywords": ["input invoice", "verifikasi tagihan", "disbursement", "pemegang kas"],
        "risk_explanation": "Risiko pembuatan vendor fiktif atau pengubahan nomor rekening vendor untuk mengalihkan dana transfer perusahaan.",
        "recommendation": "Batasi akses pengubahan master vendor hanya pada unit khusus terpisah dari bagian pembayaran.",
    },
    {
        "code": "SOD-04",
        "title": "Penagihan Piutang (Billing) vs Penerimaan Kas (Cash Collection)",
        "role_a_keywords": ["billing", "penagihan", "invoice sales"],
        "role_b_keywords": ["kasir", "cashier", "penerima kas", "bank reconciler"],
        "risk_explanation": "Risiko penyelewengan kas melalui skema lapping (menunda pencatatan penerimaan kas untuk menutupi kas yang diambil).",
        "recommendation": "Fungsi penerbitan tagihan harus terpisah dari kasir dan fungsi rekonsiliasi kas bank.",
    },
    {
        "code": "SOD-05",
        "title": "Pengembang Aplikasi TI vs Otorisator Rilis Produksi (Developer vs Deployer)",
        "role_a_keywords": ["software engineer", "developer", "programmer", "coder"],
        "role_b_keywords": ["release manager", "production deployer", "database admin", "sysadmin"],
        "risk_explanation": "Developer yang dapat mempublikasikan kode langsung ke server produksi dapat menyisipkan backdoor atau logika tanpa pengujian.",
        "recommendation": "Terapkan pipeline CI/CD dengan perlindungan branch dan persetujuan terpisah dari Release Manager.",
    },
]

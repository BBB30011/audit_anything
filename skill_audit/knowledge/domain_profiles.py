"""Universal Domain Terrain Profiles & Knowledge Repository for Multi-Terrain Auditing.

Provides rich reference frameworks, statutory citations, testing procedures,
and red flags for all 12+ audit terrains.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from skill_audit.models import AuditDomain


@dataclass(frozen=True)
class TerrainAuditProgram:
    domain: AuditDomain
    title: str
    statutory_references: list[str]
    core_objectives: list[str]
    mandatory_documents: list[str]
    key_red_flags: list[str]
    keywords: list[str]
    mandatory_obligations: list[dict[str, str]]


DOMAIN_TERRAIN_PROFILES: dict[AuditDomain, TerrainAuditProgram] = {
    AuditDomain.FINANCIAL: TerrainAuditProgram(
        domain=AuditDomain.FINANCIAL,
        title="Audit Keuangan & Pelaporan Akuntansi (Financial Audit)",
        statutory_references=[
            "Standar Akuntansi Keuangan (SAK / PSAK / IFRS)",
            "Standar Profesional Akuntan Publik (SPAP / SA 200-700)",
            "UU Nomor 40 Tahun 2007 tentang Perseroan Terbatas",
        ],
        core_objectives=[
            "Memastikan kewajaran penyajian laporan keuangan sesuai SAK/IFRS.",
            "Rekonsiliasi saldo buku besar terhadap rekening koran bank dan subledger.",
            "Uji pisah batas (cut-off) pendapatan dan beban akhir periode.",
        ],
        mandatory_documents=[
            "Laporan Posisi Keuangan (Neraca)",
            "Laporan Laba Rugi",
            "Buku Kas / Jurnal Umum",
            "Rekening Koran Bank",
            "Rekonsiliasi Bank Bulanan",
        ],
        key_red_flags=[
            "Selisih saldo buku kas terhadap rekening koran bank tanpa rekonsiliasi",
            "Jurnal penyesuaian manual (manual journal entries) bernilai material di akhir tahun",
            "Pencatatan piutang macet tanpa cadangan kerugian penurunan nilai (CKPN)",
        ],
        keywords=[
            "neraca", "laba rugi", "rekening koran", "buku besar", "trial balance",
            "jurnal", "debit", "kredit", "rekonsiliasi bank", "kas", "deposito",
        ],
        mandatory_obligations=[
            {
                "code": "OBL-FIN-001",
                "category": "Integritas Kas & Bank",
                "description": "Rekonsiliasi bank bulanan diverifikasi dan disetujui independen dari pemegang kas.",
                "statutory": "SA 505 (Konfirmasi Eksternal) & PSAK 2",
            },
            {
                "code": "OBL-FIN-002",
                "category": "Subledger Reconciliation",
                "description": "Total subledger piutang dan hutang cocok 100% dengan akun pengendali buku besar.",
                "statutory": "SA 500 (Bukti Audit)",
            },
        ],
    ),
    AuditDomain.PROCUREMENT: TerrainAuditProgram(
        domain=AuditDomain.PROCUREMENT,
        title="Audit Pengadaan Barang & Jasa (Procurement & Contracts)",
        statutory_references=[
            "Perpres No. 16 Tahun 2018 jo Perpres No. 12 Tahun 2021 tentang Pengadaan Barang/Jasa Pemerintah",
            "Pedoman Kebijakan Pengadaan LKPP",
            "UU No. 5 Tahun 1999 tentang Larangan Praktek Monopoli dan Persaingan Usaha Tidak Sehat",
        ],
        core_objectives=[
            "Memastikan pengadaan memenuhi prinsip 6T (Tepat Mutu, Jumlah, Waktu, Lokasi, Harga, Penyedia).",
            "Verifikasi 3-Way Match (Purchase Order, BAST, dan Faktur Vendor).",
            "Pencegahan tender persekongkolan (bid rigging) dan vendor terafiliasi.",
        ],
        mandatory_documents=[
            "Surat Pesanan / Kontrak / SPK",
            "Berita Acara Serah Terima (BAST)",
            "Invoice / Tagihan Rekanan",
            "Faktur Pajak (e-Faktur)",
            "Kuitansi / Bukti Bayar",
        ],
        key_red_flags=[
            "Ketidaksesuaian nilai 3-Way Match tanpa Berita Acara Perubahan Kontrak (Addendum)",
            "Penyedia memiliki alamat, pengurus, atau nomor rekening bank yang identik (kartel tender)",
            "Pemecahan paket pengadaan (splitting) di bawah ambang batas lelang langsung",
        ],
        keywords=[
            "spk", "kontrak", "bast", "invoice", "vendor", "po", "purchase order",
            "tender", "hps", "rekanan", "pengadaan", "surat pesanan",
        ],
        mandatory_obligations=[
            {
                "code": "OBL-PROC-001",
                "category": "3-Way Reconciliation",
                "description": "Nilai tagihan invoice harus cocok secara presisi dengan BAST fisik dan Kontrak/PO.",
                "statutory": "Perpres 16/2018 Pasal 57 & Tata Kelola Pengadaan",
            },
            {
                "code": "OBL-PROC-002",
                "category": "Due Diligence Rekanan",
                "description": "Verifikasi legalitas NIB, NPWP, dan rekening bank resmi rekanan.",
                "statutory": "UU HPP No. 7/2021 & Perpres 16/2018",
            },
        ],
    ),
    AuditDomain.GOVERNMENT: TerrainAuditProgram(
        domain=AuditDomain.GOVERNMENT,
        title="Audit Sektor Publik & Pemerintahan (BPK / BPKP Compliance)",
        statutory_references=[
            "UU No. 17 Tahun 2003 tentang Keuangan Negara",
            "UU No. 1 Tahun 2004 tentang Perbendaharaan Negara",
            "UU No. 15 Tahun 2004 tentang Pemeriksaan Pengelolaan dan Tanggung Jawab Keuangan Negara",
            "PP No. 71 Tahun 2010 tentang Standar Akuntansi Pemerintahan (SAP)",
        ],
        core_objectives=[
            "Memastikan realisasi belanja tidak melebihi DPA (Dokumen Pelaksanaan Anggaran).",
            "Verifikasi kelengkapan dokumen pencairan: SPP, SPM, dan SP2D.",
            "Uji kewajaran belanja modal dan pencatatan Barang Milik Daerah/Negara (BMD/BMN).",
        ],
        mandatory_documents=[
            "Dokumen Pelaksanaan Anggaran (DPA/RKA)",
            "Surat Permintaan Pembayaran (SPP)",
            "Surat Perintah Membayar (SPM)",
            "Surat Perintah Pencairan Dana (SP2D)",
            "Laporan Realisasi Anggaran (LRA)",
        ],
        key_red_flags=[
            "Penerbitan SP2D mendahului BAST atau verifikasi fisik pekerjaan",
            "Realisasi anggaran menumpuk drastis (>40%) pada bulan Desember (akhir TA)",
            "Pencatatan aset tetap belanja modal tanpa Berita Acara Rekonsiliasi Aset BMD",
        ],
        keywords=[
            "apbn", "apbd", "dpa", "rka", "sp2d", "spm", "spp", "satker", "kpa", "ppk",
            "bendahara pengeluaran", "silpa", "lra", "lkpd", "lkpp", "bpk", "bpkp", "sipd",
        ],
        mandatory_obligations=[
            {
                "code": "OBL-GOV-001",
                "category": "Kesesuaian Anggaran DPA",
                "description": "Realisasi belanja tidak melampaui sisa pagu kode rekening mata anggaran DPA.",
                "statutory": "UU 17/2003 Pasal 3 & UU 1/2004",
            },
            {
                "code": "OBL-GOV-002",
                "category": "Integritas Berkas SP2D",
                "description": "SP2D wajib didukung SPM bertandatangan PA/KPA dan Berita Acara Pembayaran sah.",
                "statutory": "UU 1/2004 Perbendaharaan Negara",
            },
        ],
    ),
    AuditDomain.HEALTHCARE: TerrainAuditProgram(
        domain=AuditDomain.HEALTHCARE,
        title="Audit Fasilitas Kesehatan & Klaim Medis (Hospital & Healthcare)",
        statutory_references=[
            "UU No. 17 Tahun 2023 tentang Kesehatan",
            "Permenkes No. 24 Tahun 2022 tentang Rekam Medis",
            "Peraturan BPJS Kesehatan tentang Pencegahan Kecurangan (Fraud)",
            "Standar Akreditasi Rumah Sakit (KARS / JCI)",
        ],
        core_objectives=[
            "Pencegahan fraud klaim BPJS (upcoding, phantom billing, repeat billing).",
            "Verifikasi rekonsiliasi stok obat narkotika dan psikotropika (SIPNAP).",
            "Kepatuhan informed consent dan kelengkapan resume medis pasien.",
        ],
        mandatory_documents=[
            "Resume Medis Pasien (Discharge Summary)",
            "Rincian Biaya Rumah Sakit (Billing Statement)",
            "Formulir Klaim BPJS / Asuransi",
            "Kartu Stok Obat Farmasi / Buku Register Narkotika",
            "Surat Persetujuan Tindakan Medis (Informed Consent)",
        ],
        key_red_flags=[
            "Kode diagnosis ICD-10 dinaikkan ke tingkat keparahan lebih tinggi tanpa dasar resume medis (upcoding)",
            "Tagihan obat/tindakan medis ditagihkan ganda untuk satu episode rawat inap (double billing)",
            "Selisih fisik obat narkotika/psikotropika terhadap buku register keluar-masuk farmasi",
        ],
        keywords=[
            "pasien", "dokter", "rumah sakit", "rsud", "klinis", "icd-10", "ina-cbg",
            "bpjs kesehatan", "klaim", "obat", "farmasi", "resep", "narkotika",
            "psikotropika", "rekam medis", "rawat inap", "rawat jalan",
        ],
        mandatory_obligations=[
            {
                "code": "OBL-HLT-001",
                "category": "Informed Consent & Resume Medis",
                "description": "Tindakan operatif dan prosedur medis wajib memiliki informed consent dan resume medis dokter DPJP.",
                "statutory": "UU Kesehatan No. 17/2023 & Permenkes 24/2022",
            },
            {
                "code": "OBL-HLT-002",
                "category": "Verifikasi Kode INA-CBGs",
                "description": "Kode diagnosis ICD-10 dan prosedur ICD-9-CM pada klaim harus didukung bukti penunjang (lab/rontgen).",
                "statutory": "Permenkes Tarif JKN & Aturan Anti-Fraud BPJS",
            },
        ],
    ),
    AuditDomain.HR_PAYROLL: TerrainAuditProgram(
        domain=AuditDomain.HR_PAYROLL,
        title="Audit Ketenagakerjaan & Penggajian (HR & Payroll Audit)",
        statutory_references=[
            "UU No. 13 Tahun 2003 jo UU No. 6 Tahun 2023 tentang Penetapan Perppu Cipta Kerja",
            "PP No. 35 Tahun 2021 tentang PKWT, Alih Daya, Waktu Kerja dan Waktu Istirahat, dan PHK",
            "PP No. 36 Tahun 2021 tentang Pengupahan",
            "UU No. 24 Tahun 2011 tentang Badan Penyelenggara Jaminan Sosial (BPJS)",
        ],
        core_objectives=[
            "Pencegahan pegawai fiktif (ghost employees) dan kebocoran dana payroll.",
            "Kepatuhan batas maksimal waktu kerja lembur (maksimal 4 jam/hari atau 18 jam/minggu).",
            "Ketepatan perhitungan pesangon PHK, iuran BPJS Ketenagakerjaan/Kesehatan, dan PPh 21 TER.",
        ],
        mandatory_documents=[
            "Daftar Rekap Gaji (Payroll Master Sheet)",
            "Rekapitulasi Absensi & Lembur (SPL)",
            "Bukti Potong PPh 21 (Form 1721-A1)",
            "Bukti Pembayaran Iuran BPJS TK & BPJS Kesehatan",
            "Surat Perjanjian Kerja (PKWT/PKWTT)",
        ],
        key_red_flags=[
            "Dua atau lebih pegawai aktif memiliki nomor rekening bank atau NIK yang identik",
            "Pegawai yang telah resign/PHK masih tercantum dan menerima transfer gaji pada bulan berikutnya",
            "Jam lembur bulanan melampaui batas maksimal regulasi tanpa persetujuan tertulis",
        ],
        keywords=[
            "karyawan", "pegawai", "gaji", "payroll", "bpjs ketenagakerjaan", "bpjs tk",
            "lembur", "overtime", "pesangon", "phk", "pkwt", "pkwtt", "absensi",
            "nik pegawai", "slip gaji", "upah minimum", "ump", "umk",
        ],
        mandatory_obligations=[
            {
                "code": "OBL-HR-001",
                "category": "Integritas Master Payroll",
                "description": "Setiap rekening penerima gaji harus unik dan terverifikasi atas nama karyawan aktif terdaftar.",
                "statutory": "Standar Kontrol Internal Penggajian & COSO",
            },
            {
                "code": "OBL-HR-002",
                "category": "Kepatuhan Waktu Lembur & Upah Minimum",
                "description": "Upah pokok memenuhi UMP/UMK dan lembur tidak melampaui batas statuter 4 jam/hari.",
                "statutory": "UU Cipta Kerja No. 6/2023 & PP 35/2021",
            },
        ],
    ),
    AuditDomain.SUPPLY_CHAIN: TerrainAuditProgram(
        domain=AuditDomain.SUPPLY_CHAIN,
        title="Audit Rantai Pasok, Logistik & Pergudangan (Supply Chain & Inventory)",
        statutory_references=[
            "PSAK 14 (Pernyataan Standar Akuntansi Keuangan tentang Persediaan)",
            "Standar Manajemen Logistik & Pergudangan Terintegrasi (WMS Standards)",
            "Ketentuan Keselamatan & Kesehatan Kerja (K3 Pergudangan)",
        ],
        core_objectives=[
            "Memastikan akurasi fisik persediaan terhadap catatan buku (Stock Opname accuracy >= 98%).",
            "Identifikasi persediaan usang, rusak, atau lambat bergerak (slow-moving/dead-stock > 180 hari).",
            "Verifikasi otorisasi mutasi keluar-masuk barang dan penyesuaian (write-off).",
        ],
        mandatory_documents=[
            "Berita Acara Stock Opname (BASO)",
            "Laporan Posisi Persediaan (Stock Ledger / WMS Report)",
            "Surat Jalan / Delivery Order (DO)",
            "Bukti Penerimaan Barang (Goods Receipt / GRN)",
            "Formulir Otorisasi Pemusnahan / Write-Off Persediaan",
        ],
        key_red_flags=[
            "Selisih material (> 2%) antara hasil hitung fisik BASO dengan saldo sistem tanpa investigasi",
            "Saldo stok bernilai negatif pada sistem inventori (menunjukkan kegagalan kontrol mutasi)",
            "Pemusnahan atau write-off persediaan bernilai tinggi tanpa persetujuan Direksi/Komite Aset",
        ],
        keywords=[
            "gudang", "warehouse", "stok", "stock opname", "persediaan", "inventory",
            "sku", "kartu stok", "dead stock", "surat jalan", "grn", "delivery order",
            "lead time", "safety stock", "write-off", "scrap",
        ],
        mandatory_obligations=[
            {
                "code": "OBL-SCM-001",
                "category": "Stock Opname Fisik",
                "description": "Stock opname fisik wajib dilaksanakan berkala dengan keterlibatan tim independen (bukan penjaga gudang).",
                "statutory": "PSAK 14 & SoD Pengendalian Fisik",
            },
            {
                "code": "OBL-SCM-002",
                "category": "Otorisasi Write-Off & Scrap",
                "description": "Pemusnahan persediaan rusak/usang harus didukung Berita Acara dan persetujuan pejabat DoA.",
                "statutory": "PSAK 14 Persediaan",
            },
        ],
    ),
    AuditDomain.FORENSIC_FRAUD: TerrainAuditProgram(
        domain=AuditDomain.FORENSIC_FRAUD,
        title="Audit Investigatif & Deteksi Fraud (Forensic Investigation)",
        statutory_references=[
            "Standar Audit Investigasi BPK RI / BPKP",
            "ACFE Fraud Tree & Forensic Accounting Standards",
            "UU No. 31 Tahun 1999 jo UU No. 20 Tahun 2001 tentang Pemberantasan Tindak Pidana Korupsi",
            "ISO 37001:2016 Sistem Manajemen Anti Penyuapan (SMAP)",
        ],
        core_objectives=[
            "Identifikasi anomali numerik menggunakan uji digital Benford's Law.",
            "Deteksi red flags suap, gratifikasi, transaksi dengan pihak terafiliasi tersembunyi.",
            "Uji transaksi pemecahan nilai (smurfing/splitting) dan transaksi di hari libur.",
        ],
        mandatory_documents=[
            "Buku Besar Transaksi Lengkap (General Ledger Dump)",
            "Rekening Koran Perusahaan & Rekening Afiliasi",
            "Daftar Vendor & Pemegang Saham Rekanan",
            "Log Transaksi Keuangan Digital & Timestamp",
            "Deklarasi Benturan Kepentingan (Conflict of Interest)",
        ],
        key_red_flags=[
            "Penyimpangan signifikan distribusi digit angka menurut hukum Benford's Law (MAD > 0.015)",
            "Banyak transaksi bulat (round numbers) persis di bawah batas otorisasi pimpinan",
            "Pencatatan pengeluaran dana dilakukan pada akhir pekan/hari libur tanpa surat tugas dinas",
            "Pengurus rekanan merupakan kerabat dekat/terafiliasi dengan pengambil keputusan",
        ],
        keywords=[
            "fraud", "investigasi", "korupsi", "suap", "gratifikasi", "kickback",
            "benford", "pihak terafiliasi", "konflik kepentingan", "vendor fiktif",
            "markup", "pencucian uang", "tindak pidana",
        ],
        mandatory_obligations=[
            {
                "code": "OBL-FRD-001",
                "category": "Analisis Distribusi Benford",
                "description": "Seluruh kumpulan data transaksi numerik wajib diuji kewajaran distribusinya via Benford's Law.",
                "statutory": "Standar Audit Investigasi ISA 240 / ACFE",
            },
            {
                "code": "OBL-FRD-002",
                "category": "Anti-Bribery & Due Diligence",
                "description": "Verifikasi deklarasi bebas benturan kepentingan untuk transaksi bernilai material.",
                "statutory": "ISO 37001:2016 SMAP",
            },
        ],
    ),
    AuditDomain.IT_SECURITY: TerrainAuditProgram(
        domain=AuditDomain.IT_SECURITY,
        title="Audit Keamanan Siber & Teknologi Informasi (ITGC / Cyber Audit)",
        statutory_references=[
            "ISO/IEC 27001:2022 Sistem Manajemen Keamanan Informasi",
            "COBIT 2019 Framework for Information & Technology Governance",
            "NIST Cybersecurity Framework (CSF 2.0)",
            "UU No. 27 Tahun 2022 tentang Pelindungan Data Pribadi (UU PDP)",
        ],
        core_objectives=[
            "Memastikan kecukupan kontrol umum TI (Change Management, Access Security, IT Operations).",
            "Verifikasi kebersihan kredensial (tanpa password plaintext, API key bocor).",
            "Uji ketahanan pencadangan data (backup recovery testing) dan retensi log minimal 12 bulan.",
        ],
        mandatory_documents=[
            "Laporan Uji Pemulihan Cadangan (Backup Restoration Test)",
            "Matriks Hak Akses Pengguna & Akun Istimewa (Privileged Users)",
            "Log Audit Transaksi & Keamanan Sistem",
            "Dokumen Permohonan Perubahan Sistem (RFC / Change Request)",
            "SOP Kebijakan Keamanan Informasi & Kebijakan Sandi",
        ],
        key_red_flags=[
            "Terdapat kredensial sensitif atau token API tersimpan dalam bentuk teks terbuka (cleartext)",
            "Akun istimewa (root/sysadmin) digunakan secara bersama-sama tanpa jejak aktivitas personal",
            "Tidak pernah dilakukan pengujian restore cadangan (backup) dalam kurun waktu 12 bulan terakhir",
        ],
        keywords=[
            "firewall", "active directory", "vpn", "iam", "rbac", "log audit",
            "backup", "restore", "patching", "cve", "sso", "mfa", "soc 2",
            "enkripsi", "database", "itgc", "cybersecurity",
        ],
        mandatory_obligations=[
            {
                "code": "OBL-IT-001",
                "category": "Uji Pemulihan Cadangan (Backup)",
                "description": "Prosedur pengujian pemulihan cadangan sistem wajib dibuktikan dengan Berita Acara berkala.",
                "statutory": "ISO 27001:2022 A.8.13 & Cobit DSS04",
            },
            {
                "code": "OBL-IT-002",
                "category": "Retensi Log Audit Sistem",
                "description": "Log aktivitas transaksi dan login akun istimewa wajib disimpan minimal 1 tahun dan terproteksi dari edit.",
                "statutory": "ISO 27001:2022 A.8.15 & UU PDP No. 27/2022",
            },
        ],
    ),
    AuditDomain.TAX_CUSTOMS: TerrainAuditProgram(
        domain=AuditDomain.TAX_CUSTOMS,
        title="Audit Perpajakan & Kepabeanan (Tax & Customs Audit)",
        statutory_references=[
            "UU No. 7 Tahun 2021 tentang Harmonisasi Peraturan Perpajakan (UU HPP)",
            "UU No. 17 Tahun 2006 tentang Kepabeanan",
            "Peraturan Menteri Keuangan tentang Tata Cara Pemotongan PPh & PPN",
        ],
        core_objectives=[
            "Memastikan kebenaran pemungutan/pemotongan PPh Pasal 21, 23, 4 ayat (2), dan PPN 11%.",
            "Verifikasi keabsahan e-Faktur Pajak Keluaran/Masukan pada sistem DJP.",
            "Uji kepatuhan dokumen pemberitahuan ekspor/impor (PEB/PIB) dan tarif pos tarif HS.",
        ],
        mandatory_documents=[
            "Surat Pemberitahuan (SPT) Masa PPN & PPh",
            "Faktur Pajak Elektronik (e-Faktur QR Code)",
            "Bukti Potong PPh 23 / 4(2) / 21",
            "Pemberitahuan Impor Barang (PIB) / PEB & Bukti Bayar Bea Masuk",
            "Buku Penjualan & Pembelian Berpajak",
        ],
        key_red_flags=[
            "Penggunaan tarif PPN lama (10%) setelah berlakunya tarif 11% sesuai UU HPP",
            "Faktur Pajak Masukan dikreditkan dari lawan transaksi yang terindikasi penerbit faktur fiktif",
            "Perbedaan omzet menurut SPT Masa PPN dengan peredaran usaha menurut SPT Tahunan PPh Badan",
        ],
        keywords=[
            "faktur pajak", "e-faktur", "spt masa", "pph 23", "pph 4(2)", "pph 21",
            "pph 25", "ppn 11%", "bea cukai", "tarif hs", "pib", "peb", "skp", "djp",
        ],
        mandatory_obligations=[
            {
                "code": "OBL-TAX-001",
                "category": "Tarif Statuter PPN 11%",
                "description": "Perhitungan PPN atas penyerahan BKP/JKP wajib menggunakan tarif 11% dan didukung e-Faktur sah.",
                "statutory": "UU HPP No. 7/2021 Pasal 7",
            },
            {
                "code": "OBL-TAX-002",
                "category": "Kewajiban Withholding Tax PPh",
                "description": "Jasa teknik/manajemen wajib dipotong PPh 23 (2%) dan dibuktikan dengan Bukti Pemotongan.",
                "statutory": "UU PPh Pasal 23 & PMK Terkait",
            },
        ],
    ),
    AuditDomain.BANKING_FINTECH: TerrainAuditProgram(
        domain=AuditDomain.BANKING_FINTECH,
        title="Audit Perbankan, Fintech & APU-PPT (Banking & AML Compliance)",
        statutory_references=[
            "UU No. 8 Tahun 2010 tentang Pencegahan dan Pemberantasan Tindak Pidana Pencucian Uang (TPPU)",
            "POJK No. 12/POJK.01/2017 tentang Penerapan Program APU PPT di Sektor Jasa Keuangan",
            "POJK tentang Tingkat Kesehatan Bank Umum & Ketentuan Likuiditas",
        ],
        core_objectives=[
            "Kepatuhan penerapan Customer Due Diligence (CDD) dan Enhanced Due Diligence (EDD).",
            "Pemantauan transaksi mencurigakan dan pencegahan pemecahan transaksi (structuring/smurfing).",
            "Akurasi perhitungan rasio kesehatan keuangan (CAR, NPL, LDR, NIM).",
        ],
        mandatory_documents=[
            "Laporan Profil Risiko Nasabah (KYC/CDD Dossier)",
            "Laporan Transaksi Keuangan Mencurigakan (LTKM / STR)",
            "Daftar Debitur & Kolektibilitas Kredit (SLIK OJK)",
            "Laporan Perhitungan CAR dan NPL Bulanan",
            "Audit Trail Sistem Transaksi Finansial",
        ],
        key_red_flags=[
            "Transaksi setoran tunai berulang persis di bawah batas wajib lapor Rp 500 juta (structuring)",
            "Nasabah berisiko tinggi (PEP / Politically Exposed Persons) tanpa persetujuan EDD pimpinan",
            "Restrukturisasi kredit bermasalah tanpa analisis kemampuan bayar yang memadai",
        ],
        keywords=[
            "nasabah", "kredit", "tabungan", "deposito", "npl", "kyc", "cdd", "edd",
            "aml", "apu ppt", "ppatk", "slik", "car", "bopo", "ldr", "likuiditas",
        ],
        mandatory_obligations=[
            {
                "code": "OBL-BNK-001",
                "category": "Customer Due Diligence (KYC)",
                "description": "Identitas seluruh nasabah terverifikasi 100% dan dilakukan penyaringan terhadap daftar DTTOT.",
                "statutory": "POJK 12/POJK.01/2017 & UU TPPU",
            },
            {
                "code": "OBL-BNK-002",
                "category": "Pelaporan Transaksi Mencurigakan",
                "description": "Transaksi dengan karakteristik smurfing/anomali wajib ditindaklanjuti dengan LTKM ke PPATK.",
                "statutory": "UU No. 8/2010 TPPU",
            },
        ],
    ),
    AuditDomain.ESG_SUSTAINABILITY: TerrainAuditProgram(
        domain=AuditDomain.ESG_SUSTAINABILITY,
        title="Audit Keberlanjutan & Lingkungan (ESG & Sustainability Audit)",
        statutory_references=[
            "POJK No. 51/POJK.03/2017 tentang Penerapan Keuangan Berkelanjutan",
            "UU No. 32 Tahun 2009 tentang Perlindungan dan Pengelolaan Lingkungan Hidup",
            "Standar Global Reporting Initiative (GRI Standards)",
        ],
        core_objectives=[
            "Verifikasi keandalan data emisi gas rumah kaca (GRK / Carbon Scope 1, 2, 3).",
            "Kepatuhan perizinan dan manifes pengelolaan limbah Bahan Berbahaya dan Beracun (Limbah B3).",
            "Keterbukaan alokasi anggaran Tanggung Jawab Sosial dan Lingkungan (TJSL / CSR).",
        ],
        mandatory_documents=[
            "Laporan Keberlanjutan Tahunan (Sustainability Report)",
            "Izin Lingkungan (AMDAL / UKL-UPL) & Manifes Limbah B3",
            "Laporan Penghitungan Emisi Karbon (GHG Inventory)",
            "Bukti Realisasi Program & Penyaluran CSR/TJSL",
            "Laporan Keselamatan & Kesehatan Kerja (K3) Lingkungan",
        ],
        key_red_flags=[
            "Klaim net-zero atau penurunan emisi tanpa metodologi kalkulasi ilmiah yang terverifikasi (greenwashing)",
            "Penyimpanan limbah B3 melampaui masa berlaku izin tanpa manifes pengangkutan resmi",
            "Ketidaksesuaian alokasi dana CSR terhadap persentase kewajiban perda/regulasi",
        ],
        keywords=[
            "esg", "keberlanjutan", "sustainability", "emisi", "karbon", "amdal",
            "limbah b3", "gri", "tjsl", "csr", "proper", "efisiensi energi",
        ],
        mandatory_obligations=[
            {
                "code": "OBL-ESG-001",
                "category": "Kepatuhan Laporan POJK 51",
                "description": "Laporan keberlanjutan diterbitkan tahunan sesuai pedoman POJK No. 51/POJK.03/2017.",
                "statutory": "POJK 51/POJK.03/2017",
            },
            {
                "code": "OBL-ESG-002",
                "category": "Legalitas Manifes Limbah B3",
                "description": "Pengelolaan dan pemusnahan limbah B3 wajib didukung manifes resmi dari KLHK.",
                "statutory": "UU 32/2009 & PP Terkait Pengelolaan Limbah",
            },
        ],
    ),
}


def get_terrain_profile(domain: AuditDomain | str) -> TerrainAuditProgram | None:
    """Retrieve detailed terrain profile for a domain."""
    if isinstance(domain, str):
        try:
            domain_enum = AuditDomain(domain.lower())
        except ValueError:
            return None
    else:
        domain_enum = domain
    return DOMAIN_TERRAIN_PROFILES.get(domain_enum)


def list_all_terrains() -> list[TerrainAuditProgram]:
    """Return all configured terrain profiles."""
    return list(DOMAIN_TERRAIN_PROFILES.values())

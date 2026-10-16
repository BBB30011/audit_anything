# Panduan Audit Teknis ITGC & Integritas Jejak Digital

Pengendalian Umum Teknologi Informasi (*IT General Controls - ITGC*) menjamin keandalan data dan integritas pemrosesan sistem aplikasi bisnis dan pelaporan keuangan.

---

## 1. Empat Pilar ITGC (The 4 Pillars of ITGC)

### A. Access to Programs and Data (AC)
- **Otentikasi Multi-Faktor (MFA)**: Wajib untuk akses admin dan VPN jarak jauh.
- **Tinjauan Akses Pengguna (User Access Review)**: Dilakukan triwulanan untuk mencabut akses berlebih.
- **Penonaktifan Akun Resign**: Integrasi proses offboarding HR dengan Active Directory/SSO (maksimal 24 jam).
- **Kata Sandi**: Panjang minimal 12 karakter, kompleksitas (huruf besar, angka, simbol), masa kedaluwarsa 90 hari.

### B. Program Changes (CH)
- **Change Management Workflow**: `Permintaan Perubahan (CR) -> Review Dampak -> Uji Coba di Staging (UAT) -> Persetujuan CAB -> Rilis Produksi`.
- **Segregation of Environments**: Server Pengembang (Dev) terisolasi dari Server Produksi (Prod).
- **Akses Pengembang**: Programmer dilarang memiliki akses tulis atau rilis langsung ke basis data produksi.

### C. Computer Operations (CO)
- **Strategi Backup 3-2-1**: 3 salinan data, 2 media berbeda, 1 lokasi off-site/cloud terpisah.
- **Restore Drill**: Uji coba pemulihan data cadangan minimal setiap 6 bulan untuk mengukur RPO (Recovery Point Objective) dan RTO (Recovery Time Objective).
- **Sinkronisasi Waktu**: Seluruh server wajib menggunakan NTP (Network Time Protocol) terpusat untuk menjaga keabsahan stempel waktu (*timestamp*) log forensik.

### D. Program Development (PD)
- Penerapan metodologi Secure SDLC.
- Pemindaian kerentanan kode otomatis (SAST/DAST) sebelum peluncuran fitur baru.

---

## 2. Verifikasi Integritas Bukti Digital (Cryptographic Grounding)
Setiap bukti audit digital (berkas laporan, ekspor CSV transaksi, atau log sistem) diverifikasi integritasnya menggunakan algoritma hash kriptografis **SHA-256**:
- Perubahan satu spasi atau digit pada file akan menghasilkan nilai hash yang sama sekali berbeda, membuktikan adanya rekayasa bukti (*evidence tampering*).

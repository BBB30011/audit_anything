# 🏛️ Skill-Audit (Auditor-Anything)

> **Enterprise Document & Audit Dossier Auditing System with Zero-Hallucination Evidence Grounding, 5-Pillar Knowledge Base, REA Architecture Integration, and Human-AI Collaborative Triage.**

[![CI Test Suite](https://img.shields.io/badge/pytest-43%20passed-brightgreen.svg)]()
[![Standards](https://img.shields.io/badge/standards-COSO%202013%20%7C%20ISO%2031000%20%7C%20ISO%2037001%20%7C%20ITGC-blue.svg)]()
[![Offline](https://img.shields.io/badge/offline-100%25%20standalone-success.svg)]()
[![Platform](https://img.shields.io/badge/platform-Antigravity%20%7C%20Claude%20Code%20%7C%20Cursor%20%7C%20CLI-purple.svg)]()

---

## 🌟 Ringkasan Eksekutif (Executive Summary)

**Skill-Audit (Auditor-Anything)** adalah sistem audit dokumen dan berkas penugasan (*audit dossier*) berbasis CLI dan Plugin Agen AI yang dirancang untuk kebutuhan auditor internal, akuntan forensik, komite audit, dan inspektorat. 

Dibangun dengan memadukan dua pilar teknologi mutakhir:
1. **[Skill-Anything](https://github.com/SYuan03/Skill-Anything)**: Ekstraksi dan pengemasan keahlian dokumen menjadi *agent skill* modular yang portabel untuk Google Antigravity, Claude Code, dan Cursor.
2. **[REA (Reverse Engineering Assistant)](https://github.com/morluto/rea)**: Metodologi forensik tingkat tinggi yang menerapkan **Ledger of Unknowns & Inquiries**, **Cryptographic Evidence Bundles (SHA-256)**, batasan keamanan konten (*untrusted content provenance*), dan **Reconstruction Obligation Ledger**.

Sistem dapat dijalankan **100% offline** menggunakan mesin analisis aturan deterministik (*heuristic rule engines*) tanpa memerlukan API key eksternal, atau dengan LLM lokal/cloud opsional untuk sintesis narasi tingkat lanjut.

---

## 🏛️ 5 Pilar Utama Fondasi Audit (Enterprise Pillars)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          5 PILAR UTAMA AUDITOR-ANYTHING                                │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. PROSES BISNIS        │ P2P, O2C, R2R, H2R, Capex & Aset, Inventory & Supply Chain   │
│ 2. TEKNIS & ITGC        │ IT General Controls (Akses, Perubahan, Operasi), SHA-256     │
│ 3. TATA KELOLA (GCG)    │ TARIF, Delegation of Authority (DoA), Anti-Bribery ISO 37001 │
│ 4. PENGENDALIAN (COSO)  │ COSO 2013 17 Prinsip, Segregation of Duties (SoD Conflicts)  │
│ 5. MANAJEMEN RISIKO     │ ISO 31000 ERM, 5x5 Likelihood x Impact Heatmap Matrix        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

1. **Proses Bisnis (*Business Processes*)**: Mengaudit siklus end-to-end:
   - **Procure-to-Pay (P2P)**: Permintaan (PR), tender, SPK/Kontrak, penerimaan fisik (BAST), verifikasi 3-Way Match, perpajakan, dan voucher pembayaran.
   - **Order-to-Cash (O2C)**: Batas kredit, delivery order, penagihan invoice & faktur pajak, rekonsiliasi piutang (*aging*).
   - **Record-to-Report (R2R)**: Jurnal penyesuaian manual, rekonsiliasi buku besar pembantu ke GL, rekonsiliasi bank harian/bulanan.
   - **Hire-to-Retire (H2R)**: Pencegahan pegawai fiktif (*ghost employee*), rekonsiliasi payroll ke HRIS, PPh 21 metode TER (PP 58/2023), BPJS.
2. **Teknis & Audit Digital (*Technical Audit & ITGC*)**:
   - 4 Domain ITGC: Akses Program & Data, Manajemen Perubahan Sistem (CAB), Operasi Komputer & Cadangan Terenkripsi (*off-site restore drill*), Secure SDLC.
   - Integritas Kriptografis: Hash SHA-256 untuk mendeteksi *tampering* berkas dan verifikasi kronologi stempel waktu (*audit trail timeline verification*).
3. **Tata Kelola Korporasi (*Corporate Governance & GRC*)**:
   - Prinsip TARIF (*Transparansi, Akuntabilitas, Responsibilitas, Independensi, Kewajaran*).
   - Penegakan Matriks Batas Wewenang (*Delegation of Authority - DoA*) bertingkat dari Supervisor hingga RUPS.
   - Standar Anti-Penyuapan SNI ISO 37001 dan pencegahan benturan kepentingan (*Conflict of Interest*).
4. **Pengendalian Internal (*Internal Controls — COSO 2013 & SoD*)**:
   - 17 Prinsip COSO dan pengujian efektivitas pengendalian (*Test of Design* & *Test of Operating Effectiveness*).
   - Pendeteksi Benturan Pemisahan Tugas (*Segregation of Duties - SoD*): Pembuat Pesanan vs Penerima Barang (BAST), Pembuat Komitmen vs Penyetuju, Pengelola Master Vendor vs Pemroses Faktur.
5. **Manajemen Risiko Keseluruhan (*ISO 31000 ERM & 5x5 Heatmap*)**:
   - Matriks 5x5 (Likelihood 1-5 x Impact 1-5).
   - Perhitungan *Inherent Risk* dan *Residual Risk* berbasis faktor efektivitas pengendalian terpasang.
   - Visualisasi kuadran: 🔴 Kritis, 🟠 Tinggi, 🟡 Sedang, 🟢 Rendah.

---

## 🤝 Alur Kolaborasi Human-AI (Human-AI Collaboration Flow)

Skill-Audit tidak menggantikan pertimbangan profesional (*professional judgement*) auditor manusia, melainkan menjadi **Co-Pilot Analitis** berkemampuan tinggi.

```
       [ AI AUDIT CO-PILOT ]                        [ HUMAN LEAD AUDITOR ]
                 │                                             │
   1. Ingest Dossier & Extractor                               │
      (PDF, Excel, Word, Text)                                 │
                 │                                             │
   2. REA Analysis & 5-Pillar Engine                           │
      • 3-Way Match & Tax Check                                │
      • SoD & DoA Breach Detection                             │
      • SHA-256 Evidence Manifest                              │
      • Compile 5C Findings & Drafts                           │
      • Open Inquiries (Unknowns Ledger)                       │
                 │                                             │
                 ├────────────────────────────────────────────►│ 3. Human Triage & Review
                 │                                             │    • skillaudit triage / Web UI
                 │                                             │    • Review & Approve 5C Drafts
                 │                                             │    • Resolve/Waive Unknowns
                 │◄────────────────────────────────────────────┤    • Adjust Risk & Add Notes
   4. Re-Synthesis & Grounding Gate                            │
      • Strict Zero-Hallucination Verifier                     │
      • Obligations Coverage Evaluation                        │
                 │                                             │
                 ├────────────────────────────────────────────►│ 5. Formal Human Sign-Off
                 │                                             │    • skillaudit signoff
                 │                                             │    • Certified Audit Opinion:
                 │                                             │      WTP / WDP / Adverse
                 ▼                                             ▼
   ┌───────────────────────────────────────────────────────────────────────────┐
   │ DELIVERABLES: LHA (MD/PDF) · KKA · Web Dashboard · Evidence Bundle · CSV  │
   └───────────────────────────────────────────────────────────────────────────┘
```

Lihat panduan lengkap di [`COLLABORATION.md`](COLLABORATION.md).

---

## 🔬 Metodologi REA (Reverse Engineering Assistant Integration)

Terinspirasi dari arsitektur [morluto/rea](https://github.com/morluto/rea):
1. **Ledger of Unknowns & Inquiries**: Ketiadaan dokumen (misal: invoice tanpa bukti transfer bank) tidak ditebak, melainkan dicatat sebagai *UnknownItem* resmi untuk diklarifikasi manajemen.
2. **Cryptographic Evidence Bundle**: Paket arsip ZIP mandiri berisi salinan dokumen, metadata ekstraksi, dan `manifest.json` bertanda tangan SHA-256 yang berkekuatan hukum di hadapan pengadilan atau regulator.
3. **Isolasi Keamanan Data**: Teks dokumen audit diberi penanda `_meta.provenance.untrusted_content` untuk melindungi model AI dari serangan injeksi instruksi tersembunyi (*prompt injection*).
4. **Audit Reconstruction & Obligation Ledger**: Pengujian ketercakupan seluruh kewajiban standar regulasi sebelum laporan dinyatakan selesai.

Lihat panduan lengkap di [`REA_METHODOLOGY.md`](REA_METHODOLOGY.md).

---

## 🚀 Instalasi & Persiapan Cepat (Quickstart)

### 1. Prasyarat
- Python 3.10+ (Diuji pada Python 3.13)
- Git

### 2. Instalasi
```bash
# Clone repository
git clone https://github.com/BBB30011/audit_anything.git
cd audit_anything

# Install dalam mode editable
pip install --no-build-isolation --no-deps -e . --break-system-packages
```

### 3. Pasang Skill ke Agen AI (Antigravity, Claude Code, Cursor)
```bash
# Otomatis memasang ke plugin Google Antigravity
skillaudit install-skill --target antigravity

# Atau salin folder skill untuk Claude Code / Cursor
skillaudit install-skill --target cursor
```

---

## 💻 Panduan Perintah CLI (CLI Usage)

### 1. Audit Berkas Keseluruhan (Dossier)
```bash
skillaudit dossier examples/procurement_dossier -f all -o output/audit_2024
```
Menghasilkan secara otomatis:
- `*_pack.yaml` (AuditPack data terstruktur)
- `*_Laporan_Hasil_Audit.md` (LHA Formal Berstandar BPK/IIA)
- `*_Kertas_Kerja_Audit.md` (KKA Prosedur Uji Substantif)
- `*_dashboard.html` (Dasbor Interaktif Offline Zero-CDN)
- `*_evidence_bundle.zip` (Cryptographic Evidence Bundle)
- `*_findings.csv` (Daftar Temuan untuk Spreadsheet)

### 2. Visualisasi Matriks Risiko 5x5 ISO 31000
```bash
skillaudit risk output/audit_2024/*_pack.yaml
```

### 3. Uji Pemisahan Tugas (SoD) & Batas Kewenangan (DoA)
```bash
skillaudit sod output/audit_2024/*_pack.yaml
skillaudit governance output/audit_2024/*_pack.yaml
```

### 4. Kelola Ledger of Unknowns (Inquiries)
```bash
# Tampilkan daftar pertanyaan terbuka
skillaudit unknowns output/audit_2024/*_pack.yaml

# Selesaikan inquiry dengan bukti pendukung
skillaudit resolve-unknown output/audit_2024/*_pack.yaml \
  --id UNK-01 \
  --notes "Telah diverifikasi terhadap rekening koran Bank Mandiri 25 Sept 2024" \
  --evidence "Rekening_Koran_Sept2024.pdf" \
  --auditor "Drs. Hendro, Ak., CA"
```

### 5. Evaluasi Ketercakupan Kewajiban Audit (Obligations)
```bash
skillaudit obligations output/audit_2024/*_pack.yaml
```

### 6. Ekspor & Verifikasi Integritas Berkas Bukti (Evidence Bundle)
```bash
# Ekspor bukti ke arsip forensik ZIP
skillaudit bundle output/audit_2024/*_pack.yaml -o evidence.zip

# Verifikasi terhadap manipulasi/tampering
skillaudit verify-bundle output/audit_2024/*_pack.yaml
```

### 7. Sesi Triage Interaktif Kolaborasi Human-AI
```bash
skillaudit triage output/audit_2024/*_pack.yaml
```

### 8. Pengesahan & Tanda Tangan Auditor Manusia
```bash
skillaudit signoff output/audit_2024/*_pack.yaml \
  --name "Drs. Bambang Wijaya, Ak., CA, CPA" \
  --role "Lead Internal Auditor" \
  --nip "NIP-19850412-201001-1-003" \
  --opinion "WDP (Wajar Dengan Pengecualian)" \
  --notes "Opini WDP diterbitkan karena ketiadaan pakta integritas rekanan pada kontrak."
```

### 9. Gerbang Validasi Ketat CI/CD (Zero-Hallucination Gate)
```bash
skillaudit verify output/audit_2024/*_pack.yaml --strict
```

---

## 📊 Dasbor Web Interaktif (Offline Interactive HTML)

Setiap penugasan menghasilkan berkas mandiri `dashboard.html` (bebas dependensi internet / zero-CDN) dengan fitur:
- **Matriks Risiko 5x5 Interaktif**: Klik kuadran untuk memfilter temuan.
- **Triage Panel Kolaborasi**: Tombol *Approve*, *Reject (False Positive)*, input catatan auditor manusia, dan unduh data hasil review (`.json`).
- **Tab Unknowns Ledger**: Pantau status klarifikasi bukti dan dokumen yang belum diperoleh.
- **Tab Audit Obligations**: Ukur pemenuhan regulasi standar.
- **Tab Rekonsiliasi 3-Way**: Tabel rincian pembanding Kontrak vs BAST vs Invoice.
- **Tab SoD & DoA**: Matriks benturan peran dan riwayat pelampauan wewenang approval.
- **Tab Evidence Forensics**: Tabel SHA-256 digest dan status integritas berkas.
- **Lembar Pengesahan Formal**: Sertifikat opini audit yang siap dicetak (*print-ready*).

---

## 🧪 Pengujian Unit & Kualitas Kode (Test Suite)

Repositori ini dilengkapi uji otomatis menyeluruh (`pytest`):
- **43 Unit Tests (100% Pass dalam 0.55s)**
- Menguji seluruh pilar:
  - Ekstraksi entitas & verifikasi kutipan bukti verbatim
  - Uji rekonsiliasi 3-Way Matching & perhitungan PPN 11%
  - Deteksi benturan pemisahan tugas (SoD) & batas otorisasi (DoA)
  - Pembentukan matriks risiko 5x5 ISO 31000
  - Pembuatan & verifikasi integritas paket bukti (Evidence Bundle)
  - Pengelolaan buku besar pertanyaan terbuka (Unknowns Ledger)
  - Sub-perintah CLI end-to-end

Jalankan test suite kapan saja:
```bash
pytest -v
```

---

## 📄 Lisensi

Didistribusikan di bawah lisensi Apache 2.0. Bebas digunakan untuk keperluan komersial, audit internal korporasi, kantor akuntan publik (KAP), maupun instansi pemerintah (APIP/BPK).

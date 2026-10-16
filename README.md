# 🏛️ Skill-Audit (Auditor-Anything)

> **Enterprise Document & Audit Dossier Auditing System with Zero-Hallucination Evidence Grounding, 5-Pillar Knowledge Base, REA Architecture Integration, and Human-AI Collaborative Triage.**

[![CI Test Suite](https://img.shields.io/badge/pytest-50%20passed-brightgreen.svg)]()
[![Standards](https://img.shields.io/badge/standards-COSO%20%7C%20ISO%2031000%20%7C%20ISO%2037001%20%7C%20Benford%20Forensics-blue.svg)]()
[![Offline](https://img.shields.io/badge/offline-100%25%20standalone-success.svg)]()
[![Platform](https://img.shields.io/badge/platform-Antigravity%20%7C%20Claude%20Code%20%7C%20Cursor%20%7C%20CLI-purple.svg)]()

---

## 🌟 Ringkasan Eksekutif (Executive Summary)

**Skill-Audit (Auditor-Anything)** adalah sistem audit dokumen dan berkas penugasan (*audit dossier*) universal ("Segala Medan") berbasis CLI dan Plugin Agen AI yang dirancang untuk kebutuhan auditor internal, akuntan forensik, inspektorat, komite audit, dan pemeriksa kepatuhan di segala sektor industri.

Dibangun dengan memadukan tiga pilar teknologi mutakhir:
1. **[Skill-Anything](https://github.com/SYuan03/Skill-Anything)**: Ekstraksi dan pengemasan keahlian audit menjadi *agent skill* modular yang portabel untuk Google Antigravity, Claude Code, dan Cursor.
2. **[REA (Reverse Engineering Assistant)](https://github.com/morluto/rea)**: Metodologi forensik tingkat tinggi yang menerapkan **Ledger of Unknowns & Inquiries**, **Cryptographic Evidence Bundles (SHA-256)**, isolasi konten (*untrusted content provenance*), dan **Reconstruction Obligation Ledger**.
3. **Forensik Digital Benford's Law & Pengenal Medan Otomatis (*Multi-Terrain Engine*)**: Analisis matematis distribusi digit (Nigrini 2012 / ISA 240) dan klasifikasi otomatis 12+ medan audit (Pengadaan, Keuangan, Sektor Publik/Pemerintah, Rumah Sakit/Kesehatan, SDM/Payroll, Supply Chain, Anti-Fraud, ITGC/Cyber, Pajak/Kepabeanan, Perbankan/Fintech, ESG/Keberlanjutan).

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

## 🌐 Kemampuan "Segala Medan" (Universal Multi-Terrain Engine)

Sistem secara cerdas mendeteksi karakteristik berkas audit dan mengaktifkan prosedur uji statuter spesifik untuk 12+ medan audit:

| Medan / Domain | Standar & Kerangka Regulasi | Prosedur Uji Spesifik |
|---|---|---|
| **`PROCUREMENT`** | Perpres 16/2018, Pedoman LKPP | Rekonsiliasi 3-Way Match (Kontrak vs BAST vs Invoice), kartel vendor, tender splitting. |
| **`FINANCIAL`** | SAK / PSAK / IFRS, SA 200-700 | Rekonsiliasi Bank bulanan, Subledger to GL, uji pisah batas (*cut-off*), jurnal manual. |
| **`GOVERNMENT`** | PP 71/2010 (SAP), UU 17/2003 Keuangan Negara | Pagu DPA/RKA, verifikasi SPP/SPM/SP2D, belanja modal vs Berita Acara Rekonsiliasi Aset BMD. |
| **`HEALTHCARE`** | UU Kesehatan 17/2023, Permenkes 24/2022 | Anti-fraud klaim BPJS, upcoding diagnosis ICD-10, rekonsiliasi obat narkotika/psikotropika, informed consent. |
| **`HR_PAYROLL`** | UU 6/2023 Cipta Kerja, PP 35/2021, PP 36/2021 | Pencegahan pegawai fiktif (*ghost employees*), batas lembur maksimal 4 jam/hari, iuran BPJS TK & PPh 21 TER. |
| **`SUPPLY_CHAIN`** | PSAK 14 Persediaan, Standar WMS | Stock Opname fisik vs catatan sistem (toleransi selisih $\le 2\%$), *dead-stock* $>180$ hari, otorisasi *write-off*. |
| **`FORENSIC_FRAUD`** | ISA 240 / SA 240, ISO 37001 SMAP | Uji distribusi Benford's Law, suap/gratifikasi, transaksi pihak terafiliasi, mutasi akhir pekan. |
| **`IT_SECURITY`** | ISO/IEC 27001:2022, COBIT 2019, NIST CSF, UU PDP | ITGC (Akses pengguna, RFC Change Management, drill uji restore backup, pembersihan plaintext password). |
| **`TAX_CUSTOMS`** | UU HPP 7/2021, UU Kepabeanan 17/2006 | Uji statuter PPN 11%, withholding PPh 21/23/4(2), verifikasi e-Faktur QR code DJP, kepatuhan PIB/PEB. |
| **`BANKING_FINTECH`** | POJK APU-PPT, UU 8/2010 TPPU | Customer Due Diligence (CDD/EDD), pemantauan transaksi terpecah (*structuring/smurfing*), rasio CAR & NPL. |
| **`ESG_SUSTAINABILITY`**| POJK 51/2017, UU 32/2009 Lingkungan Hidup | Verifikasi emisi gas rumah kaca Scope 1-3, kepatuhan manifes limbah B3, realisasi anggaran CSR/TJSL. |
| **`LEGAL_CONTRACT`** | KUHPerdata, UU ITE, Standar Perancangan Kontrak | Uji kepatuhan SLA, klausul ganti rugi (*indemnification*), batas liabilitas, penyelesaian sengketa. |

---

## 📈 Analisis Forensik Digital: Benford's Law (Nigrini 2012)

Dalam mendeteksi fabrikasi angka (*creative accounting*), faktur palsu, dan markup, engine menerapkan **Uji Distribusi Digit Pertama Benford's Law**:
$$P(d) = \log_{10}(1 + 1/d) \quad \text{untuk } d \in \{1 \dots 9\}$$

- **Mean Absolute Deviation (MAD)** dihitung secara otomatis:
  - $\text{MAD} \le 0.006$: *Close Conformity* (Sangat Alami)
  - $0.006 < \text{MAD} \le 0.012$: *Acceptable Conformity* (Wajar)
  - $0.012 < \text{MAD} \le 0.015$: *Marginally Acceptable* (Perlu Pengawasan)
  - $\text{MAD} > 0.015$: *Non-Conforming* $\rightarrow$ **Otomatis memicu Temuan 5C Anomali Forensik (`FND-BNF-001`)** dan mewajibkan uji petik substantif 100% pada transaksi dengan digit anomali!

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

### 1. Audit Anything (Universal Multi-Terrain Command)
```bash
# Menjalankan audit cerdas dengan auto-deteksi medan atau pilihan spesifik
skillaudit audit examples/procurement_dossier --domain auto -f all -o output/audit_2024
```
Menghasilkan secara otomatis:
- `*_pack.yaml` (AuditPack data terstruktur)
- `*_Laporan_Hasil_Audit.md` (LHA Formal Berstandar BPK/IIA dengan bab Benford & REA)
- `*_Kertas_Kerja_Audit.md` (KKA Prosedur Uji Substantif)
- `*_dashboard.html` (Dasbor Interaktif Offline Zero-CDN dengan visual Benford)
- `*_evidence_bundle.zip` (Cryptographic Evidence Bundle & SHA-256 Manifest)
- `*_findings.csv` (Daftar Temuan 5C untuk Spreadsheet)

### 2. Klasifikasi Medan Audit Otomatis (Terrain Detection)
```bash
# Otomatis mengidentifikasi regulasi, entitas, dan domain dossier
skillaudit terrain examples/procurement_dossier
```

### 3. Analisis Forensik Digital: Uji Benford's Law
```bash
# Uji sebaran digit pertama Nigrini (2012) untuk deteksi fabrikasi angka
skillaudit benford output/audit_2024/*_pack.yaml
```

### 4. Daftar Seluruh Program Medan Audit (Profiles)
```bash
# Melihat 12+ medan audit bawaan beserta standar hukum rujukannya
skillaudit profiles
```

### 5. Visualisasi Matriks Risiko 5x5 ISO 31000
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

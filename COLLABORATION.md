# 🤝 Panduan Kolaborasi Human-AI (Human-AI Auditing Playbook)

> **Protokol Standar Pasangan Kerja (Pair Auditing) antara Auditor Manusia dan Agen Kecerdasan Buatan (AI Co-Pilot) dalam Penugasan Audit Dokumen & Berkas Pemeriksaan.**

---

## 🎯 Filosofi Pasangan Kerja (Pair Auditing Philosophy)

Dalam standar audit profesional (IIA, ISACA, BPK, BPKP), kecerdasan buatan **bukanlah pengganti tanggung jawab hukum auditor manusia**, melainkan sebuah **pengganda kapabilitas analitis (*intelligence amplifier*)**:

| Peran | AI Audit Co-Pilot (Skill-Audit) | Lead Auditor Manusia (Human Auditor) |
|:---|:---|:---|
| **Kekuatan Utama** | Membaca ribuan halaman dalam hitungan detik, mendeteksi salah hitung 1 Rupiah, memeriksa stempel waktu, memetakan 17 prinsip COSO. | Pertimbangan profesional (*professional judgement*), evaluasi konteks bisnis, analisis itikad manajemen, tanggung jawab hukum dan etika. |
| **Karakter Output** | Draf temuan 5C terstruktur, matriks 5x5 Heatmap, daftar ketidaksesuaian, dan buku besar pertanyaan (*Unknowns Ledger*). | Keputusan penerimaan temuan, resolusi klarifikasi, penyesuaian tingkat risiko, dan pengesahan opini audit (*Sign-Off*). |
| **Prinsip Hubungan** | Mengusulkan bukti verbatim tanpa asumsi (*Zero-Hallucination*). | Memvalidasi relevansi substantif dan menetapkan sanksi/rekomendasi. |

---

## 🔄 Siklus 5 Tahapan Kolaborasi (5-Stage Collaborative Workflow)

```
       [ TAHAP 1: AI INGESTION & ANOMALY SCAN ]
       AI mengekstrak entitas, menghitung SHA-256, menguji 3-Way Match,
       mendeteksi benturan SoD, dan pelampauan batas wewenang DoA.
                          │
                          ▼
       [ TAHAP 2: INQUIRIES & UNKNOWNS LEDGER FORMULATION ]
       AI mencatat dokumen yang hilang atau tidak lengkap sebagai
       UnknownItem (misal: invoice tanpa bukti transfer bank).
                          │
                          ▼
       [ TAHAP 3: HUMAN AUDITOR TRIAGE & REVIEW ]
       Auditor manusia memeriksa draf temuan via CLI `skillaudit triage`
       atau dasbor web:
       • Approve (Setujui)
       • Reject (Tolak sebagai False Positive / Ambiguitas yang dapat diterima)
       • Adjust Risk (Ubah tingkat risiko berdasarkan konteks materialitas)
       • Catat tanggapan awal manajemen
                          │
                          ▼
       [ TAHAP 4: DETERMINISTIC VERIFICATION GATE ]
       Sistem memvalidasi ulang paket audit dengan aturan ketat:
       Seluruh temuan wajib memiliki kutipan teks sumber verbatim
       dan seluruh inquiry kritis wajib telah diselesaikan atau dilepas (*waived*).
                          │
                          ▼
       [ TAHAP 5: FORMAL HUMAN SIGN-OFF & OPINION ISSUANCE ]
       Auditor Penanggung Jawab menandatangani lembar pengesahan formal
       dengan opini audit profesional (WTP, WDP, Tidak Wajar, Disclaimer).
```

---

## 🛠️ Panduan Operasional Kolaborasi

### 1. Menjalankan Triage Melalui Terminal (CLI Triage)
Auditor manusia dapat meninjau hasil AI secara interaktif di terminal:
```bash
skillaudit triage output/penugasan_2024/aud_pack.yaml
```

Pada setiap temuan, sistem memberikan pilihan:
- **`a` (Approve)**: Menyetujui temuan AI sebagai temuan resmi penugasan.
- **`r` (Reject / False Positive)**: Menolak temuan karena terdapat pengecualian yang dibenarkan oleh regulasi khusus atau pertimbangan materialitas. Wajib menyertakan alasan penolakan.
- **`m` (Modify / Adjust)**: Menyesuaikan tingkat risiko (misal: AI menetapkan HIGH, namun manusia menurunkan ke MEDIUM karena kontrol kompensasi memadai) dan menambahkan catatan auditor.
- **`s` (Skip)**: Melewati temuan untuk ditinjau nanti.

### 2. Mengelola & Menyelesaikan Unknowns Ledger
Ketika AI menemukan bahwa suatu dokumen belum lengkap:
```bash
# 1. Tampilkan daftar pertanyaan terbuka
skillaudit unknowns output/penugasan_2024/aud_pack.yaml

# 2. Setelah auditor meminta konfirmasi ke manajemen dan menerima bukti transfer:
skillaudit resolve-unknown output/penugasan_2024/aud_pack.yaml \
  --id UNK-01 \
  --notes "Telah diperlihatkan rekening koran Bank Mandiri tanggal 25 Sept 2024 dengan nominal Rp 50.500.000 cocok." \
  --evidence "Rekening_Koran_Mandiri_Sept.pdf" \
  --auditor "Drs. Hendro Wibowo, Ak., CA, CPA"
```

Jika dokumen memang tidak diwajibkan untuk pengadaan jenis tertentu, auditor dapat melepasnya (*waive*):
```bash
# Dilakukan melalui menu interactive `skillaudit triage` -> pilihan 'waive'
```

### 3. Triage Melalui Dasbor Web Interaktif
Buka berkas `dashboard.html` di peramban web (*browser*):
1. Masuk ke tab **Temuan Audit**.
2. Pada tiap kartu temuan, klik **✓ Setujui (Approve)** atau **✗ Tolak / FP**.
3. Klik **📝 Catatan Auditor** untuk menambahkan catatan penjelas.
4. Klik tombol **💾 Unduh Data Review (JSON)** di pojok kanan atas untuk menyimpan draf hasil review.

### 4. Menerbitkan Opini & Pengesahan Formal (Sign-Off)
Setelah seluruh temuan ditinjau dan pertanyaan diselesaikan, Lead Auditor menerbitkan pengesahan:
```bash
skillaudit signoff output/penugasan_2024/aud_pack.yaml \
  --name "Drs. Bambang Wijaya, Ak., CA, CPA" \
  --role "Lead Internal Auditor" \
  --nip "NIP-19850412-201001-1-003" \
  --opinion "WDP (Wajar Dengan Pengecualian)" \
  --notes "Opini WDP diterbitkan karena ketiadaan Pakta Integritas bermeterai pada SPK, sedangkan aspek fisik dan aritmatika telah teruji wajar."
```
Perintah ini secara otomatis memperbarui `*_pack.yaml`, menyegarkan berkas laporan `*_Laporan_Hasil_Audit.md`, dan membubuhkan stempel digital pada `*_dashboard.html`.

---

## 📋 Pedoman Penetapan Opini Audit (Audit Opinion Standards)

| Kategori Opini | Kondisi Penugasan |
|:---|:---|
| **WTP (Wajar Tanpa Pengecualian / Unqualified)** | Seluruh bukti lengkap, rekonsiliasi 3-Way Match 100% klir, tidak ada benturan SoD, tidak ada pelampauan DoA, dan seluruh kepatuhan regulasi terpenuhi. |
| **WDP (Wajar Dengan Pengecualian / Qualified)** | Sebagian besar prosedur memadai, namun terdapat temuan material tertentu yang belum dapat diselesaikan (misal: keterlambatan pelaporan pajak atau ketiadaan klausul etika tertentu), namun tidak bersifat meluas (*not pervasive*). |
| **Tidak Wajar (Adverse)** | Ditemukan penyimpangan meluas, fraud, perangkapan tugas terlarang secara masif, atau selisih materialitas nominal signifikan yang merusak keandalan laporan keuangan. |
| **Menolak Memberikan Opini (Disclaimer)** | Lingkup pemeriksaan dibatasi secara signifikan (*scope limitation*), atau sebagian besar dokumen penting tidak tersedia sehingga auditor tidak dapat memperoleh bukti yang cukup dan tepat. |

---

## 💬 Templat Prompt untuk Interaksi dengan Agen AI

Gunakan format prompt berikut ketika meminta Agen AI (Antigravity / Claude Code / Cursor) melakukan audit pada proyek Anda:

### Prompt 1: Audit Berkas Pengadaan
> *"Tolong jalankan skill `document-auditor` pada folder `berkas_pengadaan_server/`. Lakukan rekonsiliasi 3-Way Matching antara SPK, BAST, dan Faktur Pajak. Periksa apakah ada benturan pemisahan tugas (SoD) antara pembuat pesanan dan penerima barang, serta hitung ulang PPN 11% dan Bea Meterai. Sajikan hasilnya dalam format 5C dan catat seluruh dokumen yang belum tersedia ke dalam Unknowns Ledger."*

### Prompt 2: Evaluasi Batas Wewenang & GCG
> *"Tolong evaluasi seluruh tanda tangan pada kontrak `Kontrak_Pekerjaan_Gedung.pdf`. Cocokkan nominal pengadaan terhadap Matriks Batas Wewenang Otorisasi (DoA). Apakah penandatangan memiliki kapasitas hukum yang sah? Periksa pula klausul Pakta Integritas anti-penyuapan sesuai SNI ISO 37001."*

### Prompt 3: Triage Hasil Temuan
> *"Saya ingin melakukan triage terhadap AuditPack `output/audit_pack.yaml`. Tolong bantu saya meninjau temuan bernilai kritis dan tinggi terlebih dahulu, berikan rekomendasi tindak lanjut 30 hari ke depan, dan siapkan rancangan lembar pengesahan formal opini WDP."*

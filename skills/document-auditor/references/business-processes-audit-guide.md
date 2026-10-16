# Panduan Audit Siklus Proses Bisnis Utama

Panduan komprehensif pengujian audit untuk siklus proses bisnis korporasi:
1. **Procure-to-Pay (P2P)**
2. **Order-to-Cash (O2C)**
3. **Record-to-Report (R2R)**
4. **Hire-to-Retire (H2R)**

---

## 1. Procure-to-Pay (P2P) — Pengadaan hingga Pembayaran
- **Alur Kritis**: `PR -> Rencana Anggaran -> Seleksi Vendor -> SPK/PO -> BAST Fisik -> Invoice & Faktur Pajak -> Payment Voucher -> Mutasi Bank`.
- **Titik Kontrol Krusial**:
  - Validitas HPS (Harga Perkiraan Sendiri) dan pembanding harga.
  - Tanggal SPK harus mendahului penyerahan fisik barang/jasa.
  - Prinsip 3-Way Matching: Qty/Harga PO == Qty BAST == Qty/Harga Tagihan.
  - Perhitungan akurat PPN 11% dan pemotongan PPh 21/22/23.

---

## 2. Order-to-Cash (O2C) — Penjualan hingga Penerimaan Kas
- **Alur Kritis**: `Pesanan Pelanggan -> Pemeriksaan Limit Kredit -> Pengiriman Barang (DO) -> Faktur Penjualan -> Piutang Dagang (AR) -> Pelunasan Bank`.
- **Titik Kontrol Krusial**:
  - Penjualan kredit diblokir otomatis jika saldo melampaui *credit limit*.
  - Pengakuan pendapatan hanya jika ada bukti tanda terima pengiriman barang yang sah (*Delivery Order signed by customer*).
  - Evaluasi penuaan piutang (*AR Aging*) dan penyisihan piutang ragu-ragu (*Allowance for Bad Debts*).

---

## 3. Record-to-Report (R2R) — Pencatatan hingga Pelaporan Keuangan
- **Alur Kritis**: `Transaksi Harian -> Sub-Buku Besar -> Jurnal Umum -> Jurnal Penyesuaian -> Neraca Saldo -> Laporan Keuangan`.
- **Titik Kontrol Krusial**:
  - Pengendalian ketat atas jurnal penyesuaian manual (*Manual Journal Entries*) menjelang tutup buku (indikasi *window dressing*).
  - Rekonsiliasi bulanan rekening koran bank oleh staf independen.
  - Rekonsiliasi subledger Piutang/Hutang/Aset Tetap ke akun pengendali Buku Besar.

---

## 4. Hire-to-Retire (H2R) — Penggajian dan Remunerasi
- **Alur Kritis**: `Rekrutmen -> Surat Keputusan (SK) Pengangkatan -> Absensi Biometrik & Lembur -> Rekap Gaji -> PPh 21/BPJS -> Transfer Kolektif`.
- **Titik Kontrol Krusial**:
  - Pencegahan *ghost employees* dengan mencocokkan data payroll terhadap master HRIS aktif.
  - Validasi lembur berdasarkan Surat Perintah Lembur (SPL) yang disahkan atasan.
  - Perhitungan pajak penghasilan PPh 21 sesuai ketentuan TER (PP No. 58/2023).

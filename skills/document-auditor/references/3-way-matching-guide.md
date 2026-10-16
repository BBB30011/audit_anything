# Panduan Uji Silang & 3-Way Matching Dokumen Pengadaan dan Keuangan

Uji silang 3-Way Matching adalah pilar pengendalian internal (internal control) vital untuk memastikan keabsahan setiap pengeluaran kas organisasi.

---

## 1. Tiga Pilar Dokumen (The 3 Pillars)
1. **Purchase Order (PO) / Surat Perintah Kerja (SPK) / Kontrak**:
   - Memuat: Otorisasi komitmen, ruang lingkup, kuantitas barang/jasa yang dipesan, harga satuan yang disepakati, tanggal kesepakatan, dan syarat pembayaran.
2. **Goods Receipt / Berita Acara Serah Terima (BAST) / Surat Jalan**:
   - Memuat: Verifikasi fisik bahwa barang/jasa benar-benar telah diterima dalam kuantitas dan kualitas yang disyaratkan oleh pejabat penerima hasil pekerjaan.
3. **Invoice / Tagihan Vendor & Faktur Pajak**:
   - Memuat: Permohonan pembayaran resmi dari rekanan dengan rincian harga, pajak, rekening tujuan, dan nomor referensi perikatan.

---

## 2. Matriks Uji Silang Utama

| Elemen yang Diuji | Sumber Dokumen 1 | Sumber Dokumen 2 | Aturan Validasi |
|:---|:---|:---|:---|
| **Kuantitas (Quantity)** | BAST / Surat Jalan | Invoice Tagihan | `Qty Invoiced <= Qty Diterima pada BAST` |
| **Harga Satuan (Price)** | SPK / Kontrak | Invoice Tagihan | `Harga Satuan Invoice == Harga Satuan Kontrak` |
| **Total Nilai** | Kontrak / SPK | Invoice Tagihan | `Total Tagihan <= Pagu Kontrak / SPK` |
| **Kronologi Tanggal** | SPK -> BAST -> Invoice | Seluruh Dokumen | `Tgl SPK <= Tgl BAST <= Tgl Invoice <= Tgl Bayar` |
| **Rekanan / Vendor** | Kontrak / Akta | Invoice & Rek. Bank | Identitas dan NPWP harus konsisten |

---

## 3. Red Flags & Anomali Uji Silang
- **Invoice Sebelum BAST**: Tagihan diterbitkan mendahului serah terima barang/jasa. Sering menandakan upaya penyerapan anggaran secara sembrono (premature billing).
- **Invoice Tanpa BAST**: Risiko transaksi pengadaan fiktif.
- **BAST Sebelum Kontrak/SPK**: Pekerjaan dilaksanakan sebelum kontrak sah dibuat (perikatan post-factum).
- **Nilai Invoice Melampaui SPK**: Tagihan lebih bayar tanpa didasari Adendum Kontrak.

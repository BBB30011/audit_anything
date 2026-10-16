# Panduan Tata Kelola (GCG), Batas Kewenangan (DoA), dan Pemisahan Tugas (SoD)

Tata kelola perusahaan yang baik (*Good Corporate Governance*) adalah sistem yang mengarahkan dan mengendalikan korporasi agar akuntabel dan memberikan nilai jangka panjang.

---

## 1. Prinsip TARIF (Prinsip Dasar GCG)
1. **Transparansi (Transparency)**: Keterbukaan informasi keuangan dan non-keuangan tepat waktu dan objektif.
2. **Akuntabilitas (Accountability)**: Pertanggungjawaban jelas atas setiap fungsi dan keputusan manajemen.
3. **Responsibilitas (Responsibility)**: Kepatuhan mutlak terhadap regulasi perundang-undangan dan norma sosial.
4. **Independensi (Independency)**: Kemandirian organ manajemen bebas dari benturan kepentingan (*conflict of interest*).
5. **Kewajaran (Fairness)**: Keadilan dan kesetaraan dalam memperlakukan hak para pemangku kepentingan.

---

## 2. Matriks Batas Kewenangan Otorisasi (Delegation of Authority / DoA)

Matriks DoA membatasi wewenang komitmen finansial berdasarkan jenjang jabatan:

| Jenjang Jabatan | Batas Opex Maksimum | Batas Capex Maksimum | Persyaratan Pengesahan |
|:---|:---:|:---:|:---:|
| **Staff / Supervisor** | $\text{Rp } 10.000.000$ | $\text{Rp } 0$ | Single Approval |
| **Department Manager** | $\text{Rp } 100.000.000$ | $\text{Rp } 50.000.000$ | Dual Approval |
| **General Manager / VP** | $\text{Rp } 500.000.000$ | $\text{Rp } 250.000.000$ | Dual Approval |
| **Direktur Terkait** | $\text{Rp } 2.500.000.000$ | $\text{Rp } 1.000.000.000$ | Bersama Direktur Keuangan |
| **Direktur Utama (CEO)** | $\text{Rp } 10.000.000.000$ | $\text{Rp } 5.000.000.000$ | Persetujuan Direksi |
| **Dewan Komisaris / RUPS** | Di atas $\text{Rp } 10\text{ M}$ | Di atas $\text{Rp } 5\text{ M}$ | Keputusan Sirkuler / RUPS |

### Aturan Ketat DoA:
- **Larangan Self-Approval**: Pemohon anggaran tidak boleh menandatangani persetujuannya sendiri.
- **Larangan Split Purchasing**: Memecah transaksi menjadi beberapa voucher agar nilainya berada di bawah batas kewenangan pejabat tertentu dilarang keras (*fraud red flag*).

---

## 3. Matriks Pemisahan Tugas (Segregation of Duties / SoD)

Untuk mencegah kecurangan dan kesalahan, fungsi-fungsi berikut **tidak boleh dirangkap oleh individu yang sama**:

| Peran A | Peran B yang Bertentangan | Risiko Fraud yang Timbul |
|:---|:---|:---|
| **Pembuat SPK / Kontrak** | **Penerima Barang / BAST** | Penerimaan barang fiktif atau mutunya diturunkan. |
| **Pemohon Dana (Inisiator)** | **Penyetuju Pembayaran (Approver)** | Pengeluaran kas tanpa kontrol supervisi (*self-dealing*). |
| **Master Vendor Administrator** | **Petugas Input Tagihan / Kasir** | Pembuatan vendor fiktif dan pengalihan rekening transfer. |
| **Petugas Penagihan (Billing)** | **Penerima Setoran Kas / Bank** | Skema gali lubang tutup lubang kas (*lapping*). |
| **Developer Sistem TI** | **Deployer Server Produksi** | Penyisipan kode berbahaya langsung ke sistem live. |
| **Pembuat Daftar Gaji (Payroll)** | **Otorisator Transfer Gaji Bank** | Pembayaran ke pegawai fiktif (*ghost employees*). |

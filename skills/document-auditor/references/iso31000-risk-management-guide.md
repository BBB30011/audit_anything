# Panduan Manajemen Risiko Terintegrasi (ISO 31000 & COSO ERM)

Manajemen risiko adalah aktivitas terkoordinasi untuk mengarahkan dan mengendalikan organisasi terkait risiko yang dihadapi demi melindungi dan menciptakan nilai tambah.

---

## 1. Matriks 5x5 Penilaian Risiko (5x5 Heatmap)

### A. Skala Kemungkinan (Likelihood - L)
| Nilai | Kategori | Frekuensi Kualitatif | Probabilitas Kuantitatif |
|:---:|:---|:---|:---:|
| **1** | Sangat Jarang (*Rare*) | Terjadi 1 kali dalam > 5 tahun | $< 5\%$ |
| **2** | Jarang (*Unlikely*) | Terjadi 1 kali dalam 2-5 tahun | $5\% - 25\%$ |
| **3** | Mungkin (*Possible*) | Terjadi 1-2 kali per tahun | $26\% - 50\%$ |
| **4** | Sering (*Likely*) | Terjadi per triwulan / kuartal | $51\% - 80\%$ |
| **5** | Hampir Pasti (*Almost Certain*) | Terjadi bulanan atau mingguan | $> 80\%$ |

### B. Skala Dampak (Impact - I)
| Nilai | Kategori | Dampak Finansial | Dampak Reputasi & Hukum |
|:---:|:---|:---|:---|
| **1** | Insignifikan | $< \text{Rp } 10.000.000$ | Keluhan internal lokal, tidak terekspos publik |
| **2** | Minor | $\text{Rp } 10\text{jt} - \text{Rp } 100\text{jt}$ | Komplain terbatas dari rekanan/pelanggan |
| **3** | Moderat | $\text{Rp } 100\text{jt} - \text{Rp } 1\text{ Miliar}$ | Sorotan media lokal, peringatan administratif |
| **4** | Mayor | $\text{Rp } 1\text{ M} - \text{Rp } 10\text{ Miliar}$ | Penyelidikan regulator, sanksi denda berat |
| **5** | Katastropik | $> \text{Rp } 10\text{ Miliar}$ | Tuntutan pidana, pembekuan izin usaha / insolvensi |

---

## 2. Inherent Risk vs Residual Risk

$$\text{Inherent Risk} = \text{Likelihood} \times \text{Impact} \quad (\text{Skor: } 1 - 25)$$

$$\text{Residual Risk} = \text{Inherent Risk} \times \left(1 - (\text{Efektivitas Kontrol} \times 0.7)\right)$$

### Zonasi Warna Heatmap:
- 🔴 **Kritis / Ekstrem (Merah, Skor $\ge 15.0$)**: Memerlukan mitigasi segera dan laporan berkala ke Direksi & Komite Audit.
- 🟠 **Tinggi / High (Oranye, Skor $10.0 - 14.9$)**: Rencana aksi mitigasi wajib dengan batas waktu penuntasan $\le 30$ hari.
- 🟡 **Sedang / Medium (Kuning, Skor $5.0 - 9.9$)**: Pengendalian operasional rutin dengan monitoring triwulanan.
- 🟢 **Rendah / Low (Hijau, Skor $< 5.0$)**: Risiko dalam batas selera risiko (*risk appetite*) yang dapat diterima.

---

## 3. Strategi Perlakuan Risiko (Risk Treatment / 4T)
1. **Tolerate / Accept**: Menerima risiko jika masih berada di bawah selera risiko.
2. **Treat / Mitigate**: Menerapkan kontrol pencegahan dan deteksi untuk menekan kemungkinan/dampak.
3. **Transfer**: Mengalihkan risiko ke pihak ketiga (asuransi atau klausul ganti rugi vendor).
4. **Terminate / Avoid**: Menghentikan aktivitas atau proses bisnis yang menghasilkan risiko di luar toleransi.

"""Knowledge repository and audit programs for core business processes.

Covers:
- Procure-to-Pay (P2P)
- Order-to-Cash (O2C)
- Record-to-Report (R2R)
- Hire-to-Retire (H2R)
- Inventory & Supply Chain
- Capital Expenditure & Asset Lifecycle (Capex)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AuditProcedure:
    code: str
    title: str
    objective: str
    key_risks: list[str]
    testing_steps: list[str]
    documents_required: list[str]
    target_role: str


@dataclass
class BusinessProcessAuditProgram:
    name: str
    cycle_code: str
    description: str
    procedures: list[AuditProcedure] = field(default_factory=list)


# ----------------------------------------------------------------------
# 1. Procure-to-Pay (P2P)
# ----------------------------------------------------------------------

P2P_PROGRAM = BusinessProcessAuditProgram(
    name="Procure-to-Pay (P2P)",
    cycle_code="P2P",
    description="Siklus pengadaan barang/jasa mulai dari permintaan pembelian, seleksi vendor, pemesanan, penerimaan, verifikasi faktur, hingga pembayaran kas.",
    procedures=[
        AuditProcedure(
            code="P2P-01",
            title="Otorisasi Permintaan Pembelian (Purchase Requisition)",
            objective="Memastikan setiap pembelian didasarkan atas kebutuhan operasional riil dan diotorisasi pejabat berwenang sesuai pagu anggaran.",
            key_risks=["Pembelian fiktif", "Pembelian tidak ekonomis", "Pembelian di luar anggaran"],
            testing_steps=[
                "Periksa apakah formulir PR telah disetujui manajer unit kerja pemohon.",
                "Bandingkan nilai PR dengan sisa pagu DPA/RKAP.",
                "Uji apakah terdapat pemecahan PR untuk menghindari kewenangan persetujuan lebih tinggi.",
            ],
            documents_required=["Purchase Requisition", "Rencana Kerja & Anggaran (RKAP)"],
            target_role="requisition",
        ),
        AuditProcedure(
            code="P2P-02",
            title="Seleksi Vendor & Kewajaran Harga (Procurement & Tender)",
            objective="Memastikan pemilihan penyedia dilakukan secara kompetitif, transparan, dan harga yang diperoleh wajar.",
            key_risks=["Kolusi penentuan pemenang", "Harga kemahalan (mark-up)", "Vendor fiktif"],
            testing_steps=[
                "Periksa ketersediaan minimal 3 penawaran harga pembanding atau bukti evaluasi tender.",
                "Uji ketersediaan dan validitas HPS (Harga Perkiraan Sendiri).",
                "Verifikasi legalitas rekanan (Akta, NIB, NPWP, PKP, dan rekening bank resmi).",
            ],
            documents_required=["HPS / OE", "Dokumen Penawaran", "Berita Acara Evaluasi"],
            target_role="contract",
        ),
        AuditProcedure(
            code="P2P-03",
            title="Perikatan Kontrak / Purchase Order Sah",
            objective="Memastikan hak dan kewajiban hukum antara pembeli dan vendor terlindungi secara mengikat.",
            key_risks=["Sengketa hukum perdata", "Spesifikasi tidak sesuai kesepakatan", "Ketiadaan sanksi denda"],
            testing_steps=[
                "Pastikan SPK/Kontrak ditandatangani sebelum tanggal pelaksanaan pekerjaan.",
                "Periksa klausul esensial: ruang lingkup, SLA waktu, denda keterlambatan (1/1000/hari), dan domisili hukum.",
                "Verifikasi keabsahan tanda tangan dan pelunasan Bea Meterai Rp 10.000.",
            ],
            documents_required=["Surat Perintah Kerja (SPK)", "Surat Perjanjian Kontrak"],
            target_role="contract",
        ),
        AuditProcedure(
            code="P2P-04",
            title="Verifikasi Penerimaan Fisik & BAST (Goods Receipt)",
            objective="Memastikan barang atau jasa yang diserahkan telah diperiksa secara fisik, jumlah, dan mutu sebelum diterima.",
            key_risks=["Penerimaan barang cacat / kurang volume", "BAST fiktif tanpa serah terima riil"],
            testing_steps=[
                "Periksa tanda tangan tim pemeriksa barang pada BAST atau Surat Jalan.",
                "Cocokkan kuantitas dan nomor seri fisik barang terhadap SPK.",
                "Verifikasi catatan inspeksi mutu atau uji fungsi (Commissioning Test).",
            ],
            documents_required=["Berita Acara Serah Terima (BAST)", "Surat Jalan / Packing List"],
            target_role="goods_receipt",
        ),
        AuditProcedure(
            code="P2P-05",
            title="Rekonsiliasi 3-Way Matching & Verifikasi Tagihan",
            objective="Memastikan pembayaran hanya diproses untuk barang/jasa yang telah diterima dan sesuai kesepakatan harga perikatan.",
            key_risks=["Overpayment", "Pembayaran ganda (duplicate payment)", "Perhitungan PPN keliru"],
            testing_steps=[
                "Lakukan pencocokan 3 arah: PO Qty/Price == BAST Qty == Invoice Qty/Price.",
                "Hitung ulang perkalian baris, DPP, dan kebenaran tarif PPN 11% / PPh Pasal 23.",
                "Pastikan tanggal invoice tidak mendahului tanggal BAST fisik.",
            ],
            documents_required=["Invoice / Tagihan", "Faktur Pajak", "BAST", "SPK/PO"],
            target_role="invoice",
        ),
        AuditProcedure(
            code="P2P-06",
            title="Pencairan Pembayaran Kas / Bank",
            objective="Memastikan pencairan dana dilakukan ke rekening vendor yang sah dan diverifikasi oleh pejabat otorisasi.",
            key_risks=["Transfer ke rekening pribadi oknum", "Pencairan tanpa otorisasi ganda (dual control)"],
            testing_steps=[
                "Verifikasi rekening penerima pada invoice sesuai dengan master data vendor terdaftar.",
                "Uji ketersediaan otorisasi ganda (Maker - Checker - Signer) pada payment voucher / banking token.",
                "Cocokkan bukti transfer bank dengan mutasi debet pada rekening koran.",
            ],
            documents_required=["Payment Voucher", "Bukti Transfer Bank", "Rekening Koran"],
            target_role="payment_proof",
        ),
    ],
)


# ----------------------------------------------------------------------
# 2. Order-to-Cash (O2C)
# ----------------------------------------------------------------------

O2C_PROGRAM = BusinessProcessAuditProgram(
    name="Order-to-Cash (O2C)",
    cycle_code="O2C",
    description="Siklus penerimaan pesanan pelanggan, pemeriksaan batas kredit, pengiriman barang/jasa, penagihan piutang, hingga penerimaan kas.",
    procedures=[
        AuditProcedure(
            code="O2C-01",
            title="Pemeriksaan Batas Kredit & Persetujuan Pesanan",
            objective="Mencegah timbulnya piutang tak tertagih dengan membatasi penjualan kredit pada batas kredit yang diotorisasi.",
            key_risks=["Bad debts / piutang macet", "Penjualan melebihi pagu kredit tanpa persetujuan"],
            testing_steps=[
                "Periksa apakah pesanan penjualan (Sales Order) memicu blokir otomatis saat melampaui credit limit.",
                "Pastikan persetujuan override limit kredit ditandatangani oleh Credit Committee / Direktur Keuangan.",
            ],
            documents_required=["Sales Order", "Credit Limit Master File"],
            target_role="sales_order",
        ),
        AuditProcedure(
            code="O2C-02",
            title="Penerbitan Surat Jalan & Bukti Tanda Terima Pelanggan",
            objective="Memastikan pengakuan pendapatan didasarkan pada penyerahan hak dan kepemilikan barang yang sah.",
            key_risks=["Pengakuan pendapatan prematur (premature revenue recognition)", "Barang hilang dalam perjalanan"],
            testing_steps=[
                "Uji keterlacakan nomor Surat Jalan (Delivery Order) terhadap tanda terima bertanda tangan pelanggan.",
                "Lakukan uji pisah batas (cut-off) 5 hari sebelum dan sesudah akhir tahun buku.",
            ],
            documents_required=["Surat Jalan (DO)", "Tanda Terima Pelanggan"],
            target_role="delivery_order",
        ),
        AuditProcedure(
            code="O2C-03",
            title="Penagihan Piutang & Pengendalian Umur Piutang (AR Aging)",
            objective="Memastikan seluruh pengiriman telah diterbitkan invoice dan piutang tertagih sesuai termin pembayaran.",
            key_risks=["Unbilled shipments (pengiriman tidak tertagih)", "Penyisihan piutang ragu-ragu tidak memadai"],
            testing_steps=[
                "Rekonsiliasi daftar barang terkirim vs daftar invoice penjualan yang diterbitkan.",
                "Review daftar umur piutang (Aging Schedule) dan evaluasi pembentukan cadangan kerugian penurunan nilai (CKPN/ECL).",
            ],
            documents_required=["Laporan Umur Piutang (AR Aging)", "Rekonsiliasi Bank"],
            target_role="receivables",
        ),
    ],
)


# ----------------------------------------------------------------------
# 3. Record-to-Report (R2R)
# ----------------------------------------------------------------------

R2R_PROGRAM = BusinessProcessAuditProgram(
    name="Record-to-Report (R2R)",
    cycle_code="R2R",
    description="Siklus pencatatan akuntansi, jurnal manual, penutupan buku periodik (period-end close), rekonsiliasi akun, dan penyusunan laporan keuangan.",
    procedures=[
        AuditProcedure(
            code="R2R-01",
            title="Pengendalian Jurnal Penyesuaian Manual (Manual Journal Entries)",
            objective="Mencegah manipulasi angka keuangan melalui jurnal manual tanpa bukti transaksi pendukung.",
            key_risks=["Fraud manipulasi laba (window dressing)", "Jurnal tanpa otorisasi pimpinan"],
            testing_steps=[
                "Uji 100% jurnal manual bernilai material (> batas materialitas) menjelang penutupan buku.",
                "Periksa apakah setiap voucher jurnal memiliki bukti pendukung dan otorisasi tertulis.",
                "Analisis jurnal akhir pekan atau jurnal dengan akun tidak lazim.",
            ],
            documents_required=["Voucher Jurnal Manual", "General Ledger", "Bukti Transaksi"],
            target_role="working_paper",
        ),
        AuditProcedure(
            code="R2R-02",
            title="Rekonsiliasi Sub-Buku Besar ke Buku Besar (Subledger to GL)",
            objective="Memastikan integritas saldo detail transaksi terhadap saldo buku besar pengendali.",
            key_risks=["Selisih pencatatan akuntansi", "Ketidakakuratan neraca saldo"],
            testing_steps=[
                "Bandingkan saldo rincian Piutang, Hutang, dan Persediaan terhadap GL Master.",
                "Periksa tindak lanjut atas selisih rekonsiliasi yang belum diselesaikan (reconciling items).",
            ],
            documents_required=["Trial Balance", "Rekonsiliasi Subledger", "Buku Besar"],
            target_role="working_paper",
        ),
        AuditProcedure(
            code="R2R-03",
            title="Rekonsiliasi Bank Bulanan",
            objective="Memastikan saldo kas di bank menurut pembukuan cocok dengan rekening koran bank eksternal.",
            key_risks=["Penyalahgunaan kas (lapping / kiting)", "Beban bank dan bunga tidak tercatat"],
            testing_steps=[
                "Verifikasi bahwa rekonsiliasi bank dibuat setiap bulan oleh staf yang tidak memegang kas/token bank.",
                "Investigasi cek beredar (outstanding checks) dan setoran dalam perjalanan (deposits in transit) berumur > 30 hari.",
            ],
            documents_required=["Rekonsiliasi Bank", "Rekening Koran Bank", "Buku Kas GL"],
            target_role="payment_proof",
        ),
    ],
)


# ----------------------------------------------------------------------
# 4. Hire-to-Retire (H2R / Payroll)
# ----------------------------------------------------------------------

H2R_PROGRAM = BusinessProcessAuditProgram(
    name="Hire-to-Retire (H2R)",
    cycle_code="H2R",
    description="Siklus pengelolaan SDM: rekrutmen, penetapan remunerasi, absensi/lembur, penggajian (payroll), pemotongan pajak PPh 21, dan terminasi.",
    procedures=[
        AuditProcedure(
            code="H2R-01",
            title="Pencegahan Pegawai Fiktif (Ghost Employees)",
            objective="Memastikan setiap individu dalam daftar gaji adalah pegawai aktif yang terdaftar secara sah.",
            key_risks=["Pembayaran gaji pegawai fiktif", "Gaji pegawai resign tetap ditransfer"],
            testing_steps=[
                "Cocokkan daftar payroll dengan data master karyawan aktif di sistem HRIS.",
                "Uji sampel pegawai yang baru keluar (terterminasi) untuk memastikan pemutusan payroll tepat waktu.",
                "Periksa kesamaan nomor rekening bank antar pegawai yang berbeda.",
            ],
            documents_required=["Daftar Gaji (Payroll Sheet)", "Master HRIS", "Bukti Transfer Kolektif"],
            target_role="payroll",
        ),
        AuditProcedure(
            code="H2R-02",
            title="Kalkulasi Upah Lembur & Pemotongan Pajak PPh 21",
            objective="Memastikan perhitungan lembur memenuhi regulasi ketenagakerjaan dan pemotongan PPh 21/BPJS akurat.",
            key_risks=["Pelanggaran UU Ketenagakerjaan", "Kurang potong pajak PPh 21 dan BPJS Ketenagakerjaan"],
            testing_steps=[
                "Uji sampel perhitungan lembur terhadap formulir Surat Perintah Lembur (SPL) dan log absensi biometrik.",
                "Hitung ulang formula PPh 21 metode TER (Tarif Efektif Rata-rata) sesuai PP No. 58/2023.",
            ],
            documents_required=["Rekap Lembur (SPL)", "Laporan PPh 21", "Bukti Potong Pajak 1721-A1"],
            target_role="payroll",
        ),
    ],
)

ALL_PROGRAMS = [P2P_PROGRAM, O2C_PROGRAM, R2R_PROGRAM, H2R_PROGRAM]
BUSINESS_PROCESSES = {prog.cycle_code: prog for prog in ALL_PROGRAMS}


def get_program(cycle_code: str) -> BusinessProcessAuditProgram | None:
    """Retrieve audit program by cycle code (e.g. 'P2P', 'O2C', 'R2R', 'H2R')."""
    for prog in ALL_PROGRAMS:
        if prog.cycle_code.upper() == cycle_code.upper():
            return prog
    return None


def get_process_info(cycle_code: str) -> dict[str, Any] | None:
    """Retrieve structured information and key controls for a business process."""
    prog = get_program(cycle_code)
    if not prog:
        return None
    return {
        "name": prog.name,
        "cycle_code": prog.cycle_code,
        "description": prog.description,
        "procedures_count": len(prog.procedures),
        "key_controls": [p.title for p in prog.procedures],
    }


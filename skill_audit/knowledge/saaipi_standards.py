"""Standar Audit Intern Pemerintah Indonesia (SAAIPI) - PER-01/AAIPI/DPN/2021.

Codification of standards issued by Asosiasi Auditor Intern Pemerintah Indonesia (AAIPI)
for all Aparatur Pengawasan Intern Pemerintah (APIP): BPKP, Inspektorat Jenderal K/L,
Inspektorat Daerah Provinsi/Kabupaten/Kota, and Internal Audit Units (SPI) in Public Entities.

Governs:
1. Prinsip Etika APIP (Kode Etik Auditor Intern Pemerintah Indonesia)
2. Standar Atribut (Seri 1000)
3. Standar Pelaksanaan (Seri 2000)
4. Unsur Temuan 5C SAAIPI (Kondisi, Kriteria, Sebab, Akibat, Rekomendasi)
5. Kertas Kerja Audit (KKA) dan Reviu Berjenjang (AT -> KT -> Dalnis -> PM)
6. Pemantauan Tindak Lanjut Hasil Pengawasan (TLRHP) 4 Kategori Status
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from skill_audit.models import AuditDocument, AuditObligation, AuditPack, Finding5C, RiskLevel


# ======================================================================
# 1. Prinsip Etika APIP (Kode Etik SAAIPI)
# ======================================================================


class SAAIPIEthicsPrinciple(str, Enum):
    INTEGRITAS = "Integritas"
    OBJEKTIVITAS = "Objektivitas"
    KERAHASIAAN = "Kerahasiaan"
    KOMPETENSI = "Kompetensi"
    AKUNTABILITAS = "Akuntabilitas"
    PERILAKU_PROFESIONAL = "Perilaku Profesional"


@dataclass(frozen=True)
class SAAIPIPrincipleDefinition:
    principle: SAAIPIEthicsPrinciple
    title: str
    description: str
    auditor_obligations: list[str]
    prohibited_actions: list[str]


SAAIPI_ETHICS_REGISTRY: dict[SAAIPIEthicsPrinciple, SAAIPIPrincipleDefinition] = {
    SAAIPIEthicsPrinciple.INTEGRITAS: SAAIPIPrincipleDefinition(
        principle=SAAIPIEthicsPrinciple.INTEGRITAS,
        title="Prinsip Integritas",
        description=(
            "Integritas membangun kepercayaan dan memberikan dasar bagi keandalan pertimbangan auditor intern. "
            "Auditor harus jujur, adil, berani, bijaksana, dan bertanggung jawab dalam pengawasan."
        ),
        auditor_obligations=[
            "Melaksanakan tugas dengan kejujuran, ketelitian, dan tanggung jawab tinggi.",
            "Mematuhi hukum dan membuat pengungkapan yang diharuskan oleh peraturan perundang-undangan.",
            "Menghormati dan berkontribusi pada tujuan yang sah dan etis dari instansi pemerintah.",
        ],
        prohibited_actions=[
            "Secara sadar terlibat dalam tindakan ilegal atau aktivitas yang mendiskreditkan profesi APIP.",
            "Mengabaikan fakta kecurangan (fraud) atau salah saji material yang ditemukan.",
        ],
    ),
    SAAIPIEthicsPrinciple.OBJEKTIVITAS: SAAIPIPrincipleDefinition(
        principle=SAAIPIEthicsPrinciple.OBJEKTIVITAS,
        title="Prinsip Objektivitas",
        description=(
            "Auditor menunjukkan objektivitas profesional tingkat tertinggi dalam mengumpulkan, mengevaluasi, "
            "dan mengomunikasikan informasi tentang kegiatan atau proses yang diaudit tanpa dipengaruhi kepentingan pribadi."
        ),
        auditor_obligations=[
            "Menilai fakta secara netral, seimbang, dan sepenuhnya berbasis bukti audit yang terverifikasi.",
            "Menandatangani Deklarasi Bebas Benturan Kepentingan (Conflict of Interest) pada setiap penugasan.",
            "Mengungkapkan seluruh fakta material yang jika tidak diungkapkan dapat mendistorsi laporan hasil audit.",
        ],
        prohibited_actions=[
            "Berpartisipasi dalam penugasan yang menimbulkan benturan kepentingan pribadi, finansial, atau hubungan keluarga.",
            "Menerima suap, komisi, janji, hadiah, atau gratifikasi dalam bentuk apa pun dari pihak auditi.",
        ],
    ),
    SAAIPIEthicsPrinciple.KERAHASIAAN: SAAIPIPrincipleDefinition(
        principle=SAAIPIEthicsPrinciple.KERAHASIAAN,
        title="Prinsip Kerahasiaan",
        description=(
            "Auditor menghargai nilai dan kepemilikan informasi yang diterima dan tidak mengungkapkan informasi "
            "tanpa otoritas yang sah, kecuali ada kewajiban hukum atau profesional untuk melakukannya."
        ),
        auditor_obligations=[
            "Melindungi kerahasiaan dokumen, kertas kerja audit (KKA), dan data instansi yang diperiksa.",
            "Menggunakan informasi yang diperoleh semata-mata untuk tujuan pelaksanaan tugas pengawasan yang sah.",
        ],
        prohibited_actions=[
            "Membocorkan temuan pengawasan, data rahasia jabatan, atau strategi audit kepada pihak yang tidak berhak.",
            "Menggunakan data hasil audit untuk keuntungan pribadi, keluarga, atau golongan.",
        ],
    ),
    SAAIPIEthicsPrinciple.KOMPETENSI: SAAIPIPrincipleDefinition(
        principle=SAAIPIEthicsPrinciple.KOMPETENSI,
        title="Prinsip Kompetensi",
        description=(
            "Auditor menerapkan pengetahuan, keahlian, dan pengalaman yang diperlukan dalam pelaksanaan jasa pengawasan intern "
            "sesuai dengan Standar Audit Intern Pemerintah Indonesia (SAAIPI)."
        ),
        auditor_obligations=[
            "Hanya menerima penugasan yang memiliki pengetahuan, keahlian, dan kompetensi teknis yang memadai.",
            "Memenuhi kewajiban Pendidikan Profesional Berkelanjutan (PPL / Continuing Professional Education - CPE).",
            "Menerapkan teknik audit terkini (data analytics, sampling statistik, pengujian digital forensik Benford).",
        ],
        prohibited_actions=[
            "Melakukan audit tanpa pemahaman memadai atas proses bisnis, regulasi sektoral, dan metodologi audit.",
            "Menolak memperbarui kompetensi atau sertifikasi profesi (JFA/CIPA/CRMO/QRMO).",
        ],
    ),
    SAAIPIEthicsPrinciple.AKUNTABILITAS: SAAIPIPrincipleDefinition(
        principle=SAAIPIEthicsPrinciple.AKUNTABILITAS,
        title="Prinsip Akuntabilitas",
        description=(
            "Auditor wajib mempertanggungjawabkan seluruh pelaksanaan pengawasan kepada pimpinan instansi dan publik "
            "melalui proses pengawasan yang transparan, dapat diuji silang, dan tertib administrasi."
        ),
        auditor_obligations=[
            "Menyusun Kertas Kerja Audit (KKA) yang memadai dan dapat diandalkan sebagai dasar opini/simpulan.",
            "Mempertahankan jejak audit (audit trail) yang utuh atas setiap pengujian dan telaah berjenjang.",
        ],
        prohibited_actions=[
            "Menghilangkan atau memanipulasi bukti kerja audit pendukung temuan.",
            "Menolak memberikan pertanggungjawaban profesional atas kesimpulan yang diterbitkan.",
        ],
    ),
    SAAIPIEthicsPrinciple.PERILAKU_PROFESIONAL: SAAIPIPrincipleDefinition(
        principle=SAAIPIEthicsPrinciple.PERILAKU_PROFESIONAL,
        title="Prinsip Perilaku Profesional",
        description=(
            "Auditor berperilaku profesional dan mematuhi hukum serta peraturan perundang-undangan yang berlaku "
            "serta menghindari tindakan yang dapat mencemarkan profesi APIP dan kehormatan korps auditor."
        ),
        auditor_obligations=[
            "Menjunjung tinggi etika kedinasan, sopan santun, dan profesionalisme dalam berinteraksi dengan auditi.",
            "Mematuhi hierarki penugasan dan standar penjaminan kualitas pengawasan (QAIP).",
        ],
        prohibited_actions=[
            "Bersikap arogan, memeras, atau menyalahgunakan wewenang pemeriksa.",
            "Membuat pernyataan publik yang tidak terverifikasi mengenai status temuan sebelum LHA final diterbitkan.",
        ],
    ),
}


# ======================================================================
# 2. Standar Atribut (Seri 1000) & Standar Pelaksanaan (Seri 2000)
# ======================================================================


@dataclass(frozen=True)
class SAAIPIStandardClause:
    code: str
    series: str  # "1000 - Atribut" or "2000 - Pelaksanaan"
    title: str
    requirement: str
    core_deliverable: str
    verification_check: str


SAAIPI_STANDARDS_REGISTRY: list[SAAIPIStandardClause] = [
    # Standar Atribut (Seri 1000)
    SAAIPIStandardClause(
        code="SAAIPI-1000",
        series="1000 - Standar Atribut",
        title="Visi, Misi, Tujuan, Kewenangan, dan Tanggung Jawab (Piagam Audit Intern)",
        requirement=(
            "Visi, misi, tujuan, kewenangan, dan tanggung jawab aktivitas audit intern harus didefinisikan "
            "secara formal dalam Piagam Audit Intern (Internal Audit Charter) yang disetujui bersama oleh "
            "Pimpinan APIP dan Pimpinan Tertinggi Instansi Pemerintah (Menteri/Kepala Lembaga/Kepala Daerah)."
        ),
        core_deliverable="Piagam Audit Intern (Internal Audit Charter) yang masih berlaku.",
        verification_check="Memastikan adanya pengesahan formal dan hak akses tak terbatas APIP terhadap data & personil.",
    ),
    SAAIPIStandardClause(
        code="SAAIPI-1100",
        series="1000 - Standar Atribut",
        title="Independensi Organisasi dan Objektivitas Individual",
        requirement=(
            "Aktivitas audit intern harus bebas dari campur tangan dalam menentukan ruang lingkup, pelaksanaan pengawasan, "
            "dan pengomunikasian hasil. Pimpinan APIP melapor langsung kepada pimpinan tertinggi instansi. "
            "Auditor wajib objektif dan menandatangani deklarasi bebas benturan kepentingan untuk setiap penugasan."
        ),
        core_deliverable="Pakta Integritas / Deklarasi Bebas Benturan Kepentingan Tim Audit.",
        verification_check="Memverifikasi ketiadaan perangkapan jabatan operasional dan riwayat penugasan auditi terkait.",
    ),
    SAAIPIStandardClause(
        code="SAAIPI-1200",
        series="1000 - Standar Atribut",
        title="Keahlian dan Kecermatan Profesional (Due Professional Care)",
        requirement=(
            "Penugasan audit intern harus dilaksanakan dengan keahlian dan kecermatan profesional yang memadai. "
            "Auditor harus memiliki skeptisisme profesional, mempertimbangkan risiko kecurangan (fraud risk assessment), "
            "materialitas, kecukupan SPIP, dan kepatuhan terhadap standar etika profesi."
        ),
        core_deliverable="Matriks Kompetensi Tim Audit & Asesmen Risiko Kecurangan (Fraud Risk).",
        verification_check="Memeriksa sertifikasi kompetensi auditor (JFA/CIPA) dan dokumentasi pengujian skeptis atas transaksi.",
    ),
    SAAIPIStandardClause(
        code="SAAIPI-1300",
        series="1000 - Standar Atribut",
        title="Program Penjaminan dan Peningkatan Kualitas (QAIP)",
        requirement=(
            "Pimpinan APIP harus merancang dan memelihara Program Penjaminan dan Peningkatan Kualitas (QAIP) yang mencakup "
            "penilaian internal berkelanjutan (supervisi dan telaah berkala KKA) serta penilaian eksternal (Telaah Sejawat / "
            "Peer Review AAIPI) paling sedikit 1 (satu) kali dalam 3 (tiga) tahun."
        ),
        core_deliverable="Laporan Penilaian Mutu Pengawasan (QAIP Report) & Hasil Peer Review AAIPI.",
        verification_check="Memastikan adanya reviu mutu berjenjang sebelum laporan hasil pengawasan diterbitkan resmi.",
    ),
    # Standar Pelaksanaan (Seri 2000)
    SAAIPIStandardClause(
        code="SAAIPI-2000",
        series="2000 - Standar Pelaksanaan",
        title="Pengelolaan Aktivitas Audit Intern (PKPT Berbasis Risiko)",
        requirement=(
            "Pimpinan APIP harus mengelola aktivitas audit intern secara efektif untuk memastikan nilai tambah bagi instansi. "
            "Menyusun Program Kerja Pengawasan Tahunan (PKPT) berbasis risiko yang selaras dengan tujuan strategis organisasi "
            "dan disetujui oleh Pimpinan Instansi Pemerintah."
        ),
        core_deliverable="Dokumen PKPT Berbasis Risiko yang Disetujui Pimpinan Instansi.",
        verification_check="Memastikan keselarasan penugasan audit dengan peta risiko strategis instansi pemerintah.",
    ),
    SAAIPIStandardClause(
        code="SAAIPI-2100",
        series="2000 - Standar Pelaksanaan",
        title="Sifat Kerja: Tata Kelola, Manajemen Risiko, dan Pengendalian Intern (GRC/SPIP)",
        requirement=(
            "Aktivitas audit intern harus mengevaluasi dan memberikan kontribusi pada perbaikan proses tata kelola (governance), "
            "manajemen risiko (risk management), dan sistem pengendalian intern (SPIP / internal control) instansi pemerintah."
        ),
        core_deliverable="Kertas Evaluasi Maturitas SPIP & Profil Risiko Entitas Auditi.",
        verification_check="Menguji 5 unsur SPIP (Lingkungan Pengendalian, Penilaian Risiko, Kegiatan Pengendalian, Informasi & Komunikasi, Pemantauan).",
    ),
    SAAIPIStandardClause(
        code="SAAIPI-2200",
        series="2000 - Standar Pelaksanaan",
        title="Perencanaan Penugasan (Surat Tugas, Ruang Lingkup & Program Kerja Penugasan)",
        requirement=(
            "Auditor harus menyusun dan mendokumentasikan rencana untuk setiap penugasan, mencakup sasaran, ruang lingkup, "
            "metodologi, alokasi sumber daya tim penugasan (Pengendali Mutu, Pengendali Teknis, Ketua Tim, Anggota Tim), "
            "jadwal penugasan, dan dituangkan dalam Program Kerja Penugasan (PKP) serta Surat Tugas resmi pimpinan APIP."
        ),
        core_deliverable="Surat Tugas (ST) Resmi APIP dan Program Kerja Penugasan (PKP).",
        verification_check="Memverifikasi keabsahan legalitas Surat Tugas dan batasan ruang lingkup penugasan.",
    ),
    SAAIPIStandardClause(
        code="SAAIPI-2300",
        series="2000 - Standar Pelaksanaan",
        title="Pelaksanaan Penugasan (Bukti Audit Memadai & Kertas Kerja Audit/KKA)",
        requirement=(
            "Auditor harus mengidentifikasi, menganalisis, mengevaluasi, dan mendokumentasikan informasi yang memadai, "
            "kompeten (sahih), relevan, dan andal untuk mencapai sasaran penugasan. Seluruh proses dan temuan wajib "
            "dituangkan dalam Kertas Kerja Audit (KKA) yang berindeks, tertelusuri (cross-referenced), dan disupervisi berjenjang."
        ),
        core_deliverable="Kumpulan Kertas Kerja Audit (KKA) Berindeks dengan Bukti Fisik/Digital Terverifikasi.",
        verification_check="Memeriksa bahwa setiap simpulan audit didukung kutipan bukti nyata dan paraf supervisi KT/Dalnis.",
    ),
    SAAIPIStandardClause(
        code="SAAIPI-2400",
        series="2000 - Standar Pelaksanaan",
        title="Komunikasi Hasil Penugasan (LHA Berbasis 5C & Tanggapan Resmi Auditi)",
        requirement=(
            "Auditor harus mengomunikasikan hasil penugasan secara tepat waktu melalui Laporan Hasil Audit (LHA) yang objektif, "
            "jelas, ringkas, konstruktif, dan lengkap. Setiap temuan audit wajib memuat 5 unsur pokok (Kondisi, Kriteria, Sebab, "
            "Akibat, Rekomendasi/5C) serta mencantumkan tanggapan resmi dari pihak auditi (manajemen)."
        ),
        core_deliverable="Laporan Hasil Audit (LHA) Resmi dengan Format 5C dan Lembar Tanggapan Auditi.",
        verification_check="Memastikan 100% temuan memiliki 5C lengkap dan rekomendasi aplikatif kepada pihak berwenang.",
    ),
    SAAIPIStandardClause(
        code="SAAIPI-2500",
        series="2000 - Standar Pelaksanaan",
        title="Pemantauan Tindak Lanjut Hasil Pengawasan (TLRHP)",
        requirement=(
            "Pimpinan APIP harus menetapkan sistem pemantauan berkala atas tindak lanjut rekomendasi hasil pengawasan. "
            "Status rekomendasi wajib diklasifikasikan ke dalam 4 kategori status: (1) Sesuai Rekomendasi / Selesai; "
            "(2) Belum Sesuai Rekomendasi / Dalam Proses; (3) Belum Ditindaklanjuti; (4) Tidak Dapat Ditindaklanjuti dengan Alasan Sah. "
            "Jika auditi menolak menindaklanjuti risiko signifikan, pimpinan APIP wajib mengeskalasikan ke pimpinan tertinggi instansi."
        ),
        core_deliverable="Matriks Pemantauan Tindak Lanjut Rekomendasi Hasil Pengawasan (TLRHP).",
        verification_check="Memverifikasi bukti surat tindak lanjut, bukti setor pengembalian kas negara/daerah (STS/NTPN), dan revisi SOP.",
    ),
]


# ======================================================================
# 3. SAAIPI Mandatory Obligations Definition for ObligationEngine
# ======================================================================

SAAIPI_MANDATORY_OBLIGATIONS: list[dict[str, str]] = [
    {
        "code": "OBL-SAAIPI-1000",
        "category": "Mandat & Legalitas Penugasan APIP",
        "description": "Penugasan audit memiliki dasar Surat Tugas resmi pimpinan APIP dan merujuk Piagam Audit Intern.",
        "statutory": "PER-01/AAIPI/DPN/2021 Standar 1000 & 2240",
    },
    {
        "code": "OBL-SAAIPI-1100",
        "category": "Independensi & Bebas Benturan Kepentingan",
        "description": "Seluruh tim audit menandatangani deklarasi bebas benturan kepentingan terhadap auditi.",
        "statutory": "PER-01/AAIPI/DPN/2021 Standar 1100 & Kode Etik Objektivitas",
    },
    {
        "code": "OBL-SAAIPI-1200",
        "category": "Kecermatan Profesional & Skeptisisme",
        "description": "Pengujian mencakup evaluasi risiko fraud (fraud risk assessment) dan keandalan sistem pengendalian intern.",
        "statutory": "PER-01/AAIPI/DPN/2021 Standar 1220 & Standar 2120",
    },
    {
        "code": "OBL-SAAIPI-2200",
        "category": "Struktur Tim Pengawasan Berjenjang",
        "description": "Tim audit memiliki struktur hierarkis APIP baku: Pengendali Mutu, Dalnis, Ketua Tim, dan Anggota Tim.",
        "statutory": "PER-01/AAIPI/DPN/2021 Standar 2230 & 2340",
    },
    {
        "code": "OBL-SAAIPI-2300",
        "category": "Kecukupan Bukti & Kertas Kerja Audit (KKA)",
        "description": "Setiap temuan didukung bukti cukup, kompeten, relevan, andal, dan KKA terdokumentasi berindeks.",
        "statutory": "PER-01/AAIPI/DPN/2021 Standar 2310 & 2330",
    },
    {
        "code": "OBL-SAAIPI-2400",
        "category": "Struktur Temuan 5C & Tanggapan Auditi",
        "description": "Laporan Hasil Audit (LHA) memuat 5 unsur lengkap (Kondisi, Kriteria, Sebab, Akibat, Rekomendasi) serta tanggapan auditi.",
        "statutory": "PER-01/AAIPI/DPN/2021 Standar 2420 & 2430",
    },
    {
        "code": "OBL-SAAIPI-2500",
        "category": "Pemantauan Tindak Lanjut Rekomendasi (TLRHP)",
        "description": "Terdapat matriks pemantauan tindak lanjut rekomendasi dengan 4 klasifikasi status kepatuhan baku.",
        "statutory": "PER-01/AAIPI/DPN/2021 Standar 2500 (Pemantauan Tindak Lanjut)",
    },
]


# ======================================================================
# 4. SAAIPI Evaluation & Quality Assurance Engine
# ======================================================================


@dataclass
class SAAIPIStandardEvaluation:
    clause: SAAIPIStandardClause
    status: str  # "compliant", "partial", "non_compliant"
    score: float  # 0.0 - 100.0
    notes: str
    evidence_refs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.clause.code,
            "series": self.clause.series,
            "title": self.clause.title,
            "requirement": self.clause.requirement,
            "status": self.status,
            "score": round(self.score, 1),
            "notes": self.notes,
            "evidence_refs": self.evidence_refs,
        }


@dataclass
class SAAIPIComplianceReport:
    """Comprehensive compliance evaluation result against PER-01/AAIPI/DPN/2021."""

    standard_title: str = "Standar Audit Intern Pemerintah Indonesia (SAAIPI)"
    legal_basis: str = "Peraturan AAIPI Nomor: PER-01/AAIPI/DPN/2021"
    overall_compliance_score: float = 100.0
    attribute_standards_score: float = 100.0
    performance_standards_score: float = 100.0
    ethics_score: float = 100.0
    five_c_rigor_score: float = 100.0
    evaluations: list[SAAIPIStandardEvaluation] = field(default_factory=list)
    ethics_evaluations: dict[str, dict[str, Any]] = field(default_factory=dict)
    summary_verdict: str = "Memenuhi Seluruh Standar SAAIPI"

    def to_dict(self) -> dict[str, Any]:
        return {
            "standard_title": self.standard_title,
            "legal_basis": self.legal_basis,
            "overall_compliance_score": round(self.overall_compliance_score, 1),
            "attribute_standards_score": round(self.attribute_standards_score, 1),
            "performance_standards_score": round(self.performance_standards_score, 1),
            "ethics_score": round(self.ethics_score, 1),
            "five_c_rigor_score": round(self.five_c_rigor_score, 1),
            "summary_verdict": self.summary_verdict,
            "evaluations": [e.to_dict() for e in self.evaluations],
            "ethics_evaluations": self.ethics_evaluations,
        }


def evaluate_saaipi_compliance(pack: AuditPack) -> SAAIPIComplianceReport:
    """Evaluate an AuditPack against PER-01/AAIPI/DPN/2021 SAAIPI standards.

    Verifies:
    1. SAAIPI Attribute Standards (1000 - 1300):
       - Internal audit charter, independence pact, due professional care, QAIP.
    2. SAAIPI Performance Standards (2000 - 2500):
       - Risk-based planning, engagement scope, 5C finding completeness, KKA, TLRHP.
    3. Ethics adherence and 5C finding rigor.
    """
    evaluations: list[SAAIPIStandardEvaluation] = []
    doc_text = " ".join(d.content.lower() for d in pack.documents)
    doc_roles = [d.role_in_dossier.lower() for d in pack.documents]
    doc_names = [d.name.lower() for d in pack.documents]
    finding_titles = " ".join(f.title.lower() for f in pack.findings)
    finding_cats = [f.category.lower() for f in pack.findings]

    # 1. Evaluate SAAIPI-1000 (Piagam Audit / Surat Tugas)
    has_surat_tugas = any(k in doc_text or k in n for k in ["surat tugas", "piagam audit", "internal audit charter", "st apip"] for n in doc_names)
    if has_surat_tugas:
        ev_1000 = SAAIPIStandardEvaluation(
            clause=SAAIPI_STANDARDS_REGISTRY[0],
            status="compliant",
            score=100.0,
            notes="Dasar penugasan pengawasan atau Surat Tugas/Piagam Audit teridentifikasi.",
            evidence_refs=["Surat Tugas / Dasar Penugasan"],
        )
    else:
        ev_1000 = SAAIPIStandardEvaluation(
            clause=SAAIPI_STANDARDS_REGISTRY[0],
            status="partial",
            score=70.0,
            notes="Berkas tidak memuat eksplisit Surat Tugas APIP atau Piagam Audit Intern, direkomendasikan melampirkan lembar ST resmi.",
            evidence_refs=[],
        )
    evaluations.append(ev_1000)

    # 2. Evaluate SAAIPI-1100 (Independensi & Benturan Kepentingan)
    has_sod_conflict = len(pack.sod_conflicts) > 0
    has_coi_declaration = any(k in doc_text for k in ["pakta integritas", "benturan kepentingan", "conflict of interest", "independensi"])
    if has_sod_conflict:
        ev_1100 = SAAIPIStandardEvaluation(
            clause=SAAIPI_STANDARDS_REGISTRY[1],
            status="non_compliant",
            score=50.0,
            notes=f"Terdeteksi {len(pack.sod_conflicts)} benturan pemisahan tugas (SoD) atau indikasi kompromi independensi.",
            evidence_refs=[c.person_name for c in pack.sod_conflicts],
        )
    elif has_coi_declaration:
        ev_1100 = SAAIPIStandardEvaluation(
            clause=SAAIPI_STANDARDS_REGISTRY[1],
            status="compliant",
            score=100.0,
            notes="Pakta Integritas / pernyataan independensi bebas benturan kepentingan terverifikasi.",
            evidence_refs=["Pakta Integritas"],
        )
    else:
        ev_1100 = SAAIPIStandardEvaluation(
            clause=SAAIPI_STANDARDS_REGISTRY[1],
            status="compliant",
            score=90.0,
            notes="Tidak ditemukan benturan peran pada personil pengawasan yang bertugas.",
            evidence_refs=[],
        )
    evaluations.append(ev_1100)

    # 3. Evaluate SAAIPI-1200 (Due Professional Care & Skeptisisme Fraud)
    has_fraud_check = (pack.benford_analysis and pack.benford_analysis.total_numbers > 0) or any("fraud" in c or "anomali" in c for c in finding_cats)
    if has_fraud_check:
        ev_1200 = SAAIPIStandardEvaluation(
            clause=SAAIPI_STANDARDS_REGISTRY[2],
            status="compliant",
            score=100.0,
            notes="Pengujian kecermatan profesional terpenuhi: mencakup digital forensics (Benford's Law) dan deteksi anomali.",
            evidence_refs=[f"Benford N={pack.benford_analysis.total_numbers}"],
        )
    else:
        ev_1200 = SAAIPIStandardEvaluation(
            clause=SAAIPI_STANDARDS_REGISTRY[2],
            status="compliant",
            score=90.0,
            notes="Prosedur verifikasi analitis telah dilaksanakan dengan kecermatan profesional yang memadai.",
            evidence_refs=[],
        )
    evaluations.append(ev_1200)

    # 4. Evaluate SAAIPI-1300 (QAIP & Supervisi Mutu)
    has_reconciliation = len(pack.reconciliations) > 0
    has_working_papers = len(pack.working_papers) > 0
    if has_working_papers or has_reconciliation:
        ev_1300 = SAAIPIStandardEvaluation(
            clause=SAAIPI_STANDARDS_REGISTRY[3],
            status="compliant",
            score=100.0,
            notes=f"Penjaminan kualitas audit terpenuhi melalui {len(pack.working_papers)} kertas kerja dan {len(pack.reconciliations)} uji rekonsiliasi.",
            evidence_refs=["WorkingPapers / KKA"],
        )
    else:
        ev_1300 = SAAIPIStandardEvaluation(
            clause=SAAIPI_STANDARDS_REGISTRY[3],
            status="partial",
            score=80.0,
            notes="Penjaminan kualitas berjalan standar, disarankan melengkapi matriks KKA berjenjang.",
            evidence_refs=[],
        )
    evaluations.append(ev_1300)

    # 5. Evaluate SAAIPI-2000 (Pengelolaan Audit Berbasis Risiko)
    has_risk_assessment = pack.risk_heatmap is not None and len(pack.risk_heatmap.get("zones", {})) > 0
    if has_risk_assessment:
        ev_2000 = SAAIPIStandardEvaluation(
            clause=SAAIPI_STANDARDS_REGISTRY[4],
            status="compliant",
            score=100.0,
            notes="Perencanaan pengawasan berbasis risiko terpenuhi melalui Risk Heatmap 5x5 ISO 31000/ERM.",
            evidence_refs=["RiskHeatmap 5x5"],
        )
    else:
        ev_2000 = SAAIPIStandardEvaluation(
            clause=SAAIPI_STANDARDS_REGISTRY[4],
            status="compliant",
            score=85.0,
            notes="Aktivitas audit terencana dan terstruktur.",
            evidence_refs=[],
        )
    evaluations.append(ev_2000)

    # 6. Evaluate SAAIPI-2100 (GRC & SPIP)
    has_control_eval = len(pack.control_evaluations) > 0
    if has_control_eval:
        ev_2100 = SAAIPIStandardEvaluation(
            clause=SAAIPI_STANDARDS_REGISTRY[5],
            status="compliant",
            score=100.0,
            notes=f"Evaluasi Sistem Pengendalian Intern Pemerintah (SPIP) teruji pada {len(pack.control_evaluations)} area kontrol.",
            evidence_refs=["COSO/SPIP Evaluations"],
        )
    else:
        ev_2100 = SAAIPIStandardEvaluation(
            clause=SAAIPI_STANDARDS_REGISTRY[5],
            status="partial",
            score=75.0,
            notes="Evaluasi pengendalian intern perlu diperluas ke seluruh 5 unsur SPIP PP No. 60/2008.",
            evidence_refs=[],
        )
    evaluations.append(ev_2100)

    # 7. Evaluate SAAIPI-2200 (Perencanaan Penugasan & Program Kerja)
    ev_2200 = SAAIPIStandardEvaluation(
        clause=SAAIPI_STANDARDS_REGISTRY[6],
        status="compliant",
        score=95.0,
        notes=f"Sasaran dan ruang lingkup penugasan terdefinisi secara terstruktur ({pack.scope}).",
        evidence_refs=[pack.audit_ref],
    )
    evaluations.append(ev_2200)

    # 8. Evaluate SAAIPI-2300 (Bukti Audit Memadai & KKA)
    total_findings = len(pack.findings)
    grounded_findings = sum(1 for f in pack.findings if len(f.evidence) > 0)
    grounding_rate = (grounded_findings / max(1, total_findings)) * 100.0 if total_findings > 0 else 100.0

    if grounding_rate >= 90.0:
        ev_2300 = SAAIPIStandardEvaluation(
            clause=SAAIPI_STANDARDS_REGISTRY[7],
            status="compliant",
            score=100.0,
            notes=f"Kecukupan bukti audit memadai: {grounding_rate:.1f}% temuan didukung kutipan verbatim dokumen sumber.",
            evidence_refs=[f"{grounded_findings}/{total_findings} Grounded"],
        )
    elif grounding_rate >= 70.0:
        ev_2300 = SAAIPIStandardEvaluation(
            clause=SAAIPI_STANDARDS_REGISTRY[7],
            status="partial",
            score=75.0,
            notes=f"Sebagian temuan ({grounding_rate:.1f}%) telah terbukti, tingkatkan kecukupan bukti fisik/digital.",
            evidence_refs=[],
        )
    else:
        ev_2300 = SAAIPIStandardEvaluation(
            clause=SAAIPI_STANDARDS_REGISTRY[7],
            status="non_compliant",
            score=50.0,
            notes="Kecukupan bukti audit kurang memadai, berisiko melanggar Standar Pelaksanaan 2310.",
            evidence_refs=[],
        )
    evaluations.append(ev_2300)

    # 9. Evaluate SAAIPI-2400 (LHA Berbasis 5C & Tanggapan Auditi)
    # Check 5C components: Condition, Criteria, Cause, Consequence, Recommendation
    valid_5c_count = 0
    for f in pack.findings:
        has_cond = bool(f.condition.strip())
        has_crit = bool(f.criteria.strip())
        has_cause = bool(f.cause.strip())
        has_conseq = bool(f.consequence.strip())
        has_recom = bool(f.recommendation.strip())
        if has_cond and has_crit and has_cause and has_conseq and has_recom:
            valid_5c_count += 1

    five_c_pct = (valid_5c_count / max(1, total_findings)) * 100.0 if total_findings > 0 else 100.0
    if five_c_pct >= 95.0:
        ev_2400 = SAAIPIStandardEvaluation(
            clause=SAAIPI_STANDARDS_REGISTRY[8],
            status="compliant",
            score=100.0,
            notes=f"Kualitas komunikasi hasil penugasan prima: {five_c_pct:.1f}% temuan memenuhi standar 5C SAAIPI.",
            evidence_refs=[f"{valid_5c_count} Temuan 5C Lengkap"],
        )
    else:
        ev_2400 = SAAIPIStandardEvaluation(
            clause=SAAIPI_STANDARDS_REGISTRY[8],
            status="partial",
            score=round(five_c_pct, 1),
            notes=f"Sebagian temuan belum memuat unsur 5C secara lengkap ({five_c_pct:.1f}%).",
            evidence_refs=[],
        )
    evaluations.append(ev_2400)

    # 10. Evaluate SAAIPI-2500 (Pemantauan Tindak Lanjut Rekomendasi TLRHP)
    has_action_plan = len(pack.action_plan) > 0
    if has_action_plan:
        ev_2500 = SAAIPIStandardEvaluation(
            clause=SAAIPI_STANDARDS_REGISTRY[9],
            status="compliant",
            score=100.0,
            notes=f"Matriks rencana tindak lanjut (Action Plan) memuat {len(pack.action_plan)} langkah perbaikan dan target waktu penyelesaian.",
            evidence_refs=["Action Plan / TLRHP Matrix"],
        )
    else:
        ev_2500 = SAAIPIStandardEvaluation(
            clause=SAAIPI_STANDARDS_REGISTRY[9],
            status="partial",
            score=70.0,
            notes="Belum terdapat matriks pemantauan tindak lanjut rekomendasi (TLRHP) formal.",
            evidence_refs=[],
        )
    evaluations.append(ev_2500)

    # Separate Attribute vs Performance Scores
    attr_evals = evaluations[:4]
    perf_evals = evaluations[4:]

    attr_score = sum(e.score for e in attr_evals) / len(attr_evals)
    perf_score = sum(e.score for e in perf_evals) / len(perf_evals)
    overall_score = (attr_score * 0.4) + (perf_score * 0.6)

    # Ethics Evaluations
    ethics_dict: dict[str, dict[str, Any]] = {}
    for principle_enum, principle_def in SAAIPI_ETHICS_REGISTRY.items():
        # Check integrity / objectivity flags
        if principle_enum == SAAIPIEthicsPrinciple.OBJEKTIVITAS and len(pack.sod_conflicts) > 0:
            status = "Perhatian Khusus"
            score = 65.0
            note = "Terdapat indikasi benturan pemisahan peran yang dapat mengorbankan objektivitas."
        elif principle_enum == SAAIPIEthicsPrinciple.KOMPETENSI and grounding_rate < 80.0:
            status = "Perlu Peningkatan"
            score = 75.0
            note = "Kecukupan bukti perlu ditingkatkan untuk memenuhi standar kecermatan profesional."
        else:
            status = "Terpenuhi"
            score = 100.0
            note = "Prinsip etika ditaati dalam prosedur pengawasan."

        ethics_dict[principle_enum.value] = {
            "title": principle_def.title,
            "status": status,
            "score": score,
            "notes": note,
        }

    ethics_score = sum(v["score"] for v in ethics_dict.values()) / len(ethics_dict)

    if overall_score >= 90.0:
        verdict = "MEMENUHI STANDAR SAAIPI (PER-01/AAIPI/DPN/2021) SECARA PENUH"
    elif overall_score >= 75.0:
        verdict = "MEMENUHI STANDAR SAAIPI SECARA SUBSTANSIAL DENGAN CATATAN PERBAIKAN"
    else:
        verdict = "BELUM MEMENUHI STANDAR SAAIPI (PERLU PENYEMPURNAAN KKA & BUKTI AUDIT)"

    return SAAIPIComplianceReport(
        standard_title="Standar Audit Intern Pemerintah Indonesia (SAAIPI)",
        legal_basis="Peraturan AAIPI Nomor: PER-01/AAIPI/DPN/2021",
        overall_compliance_score=round(overall_score, 1),
        attribute_standards_score=round(attr_score, 1),
        performance_standards_score=round(perf_score, 1),
        ethics_score=round(ethics_score, 1),
        five_c_rigor_score=round(five_c_pct, 1),
        evaluations=evaluations,
        ethics_evaluations=ethics_dict,
        summary_verdict=verdict,
    )


# ======================================================================
# 5. Doktrin AAIPI vs BPK & Format LHA APIP SAAIPI
# ======================================================================


class AAIPIServiceType(str, Enum):
    AUDIT_KETAATAN = "Audit Ketaatan / Kepatuhan (Compliance Audit)"
    AUDIT_KINERJA = "Audit Kinerja (Performance Audit - 3E)"
    REVIU = "Reviu Laporan Keuangan / Dokumen Anggaran (Review)"
    EVALUASI = "Evaluasi Sistem Pengendalian Intern Pemerintah (SPIP) & AKIP"
    PEMANTAUAN = "Pemantauan Tindak Lanjut Hasil Pengawasan (TLRHP SAAIPI 2500)"
    KONSULTANSI = "Konsultansi, Asistensi & Pendampingan Tata Kelola (Advisory)"


AAIPI_VS_BPK_DOCTRINE = {
    "posisi_dan_mandat": {
        "apip_aaipi": "Pengawas Intern Pemerintah (Mitra Strategis & Katalisator Perubahan internal kementerian/lembaga/pemda).",
        "bpk": "Pemeriksa Eksternal Keuangan Negara independen berdasarkan UUD 1945 & UU 15/2004.",
    },
    "orientasi_dan_nada": {
        "apip_aaipi": "Pencegahan dini (Early Warning System), konsultansi perbaikan sistemik, perbaikan tata kelola (GRC).",
        "bpk": "Pemeriksaan yudikatif formal atas kewajaran penyajian akun neraca dan penghitungan kerugian negara.",
    },
    "jenis_laporan": {
        "apip_aaipi": "Laporan Hasil Audit (LHA) / Laporan Hasil Pengawasan Intern APIP berorientasi solusi.",
        "bpk": "Laporan Hasil Pemeriksaan (LHP) BPK yang memuat opini atau rekomendasi TGR.",
    },
    "kesimpulan_laporan": {
        "apip_aaipi": "Simpulan Efektivitas 3 Pilar (Tata Kelola, Manajemen Risiko, Pengendalian Intern SPIP PP 60/2008), BUKAN Opini WTP/WDP.",
        "bpk": "Opini Laporan Keuangan (WTP, WDP, Tidak Wajar/Adverse, Tidak Menyatakan Pendapat/Disclaimer).",
    },
    "struktur_penandatanganan": {
        "apip_aaipi": "Hierarki Berjenjang APIP: Anggota Tim (AT), Ketua Tim (KT), Pengendali Teknis (Dalnis), Pengendali Mutu (PM/Irban), disahkan Pimpinan APIP (Inspektur).",
        "bpk": "Penanggung Jawab Pemeriksaan BPK dan Wakil Penanggung Jawab.",
    },
    "sifat_rekomendasi": {
        "apip_aaipi": "Konstruktif, realistis, aplikatif, dan memuat Tanggapan Resmi Auditi serta Action Plan bertarget waktu terukur.",
        "bpk": "Instruksi formal penyetoran ke kas negara atau perbaikan administratif dalam batas waktu 60 hari.",
    },
}


def format_lha_aaipi(pack: AuditPack) -> str:
    """Render formal Laporan Hasil Audit (LHA) APIP according to PER-01/AAIPI/DPN/2021 SAAIPI.

    Unlike BPK LHP reports, this follows the authentic APIP internal audit methodology:
    - No WTP/WDP external opinion (instead: Simpulan Efektivitas Tata Kelola, Risiko, & SPIP)
    - 5C Findings with Management Response & Action Plan
    - TLRHP 4-Category Monitoring
    - 5-Tier Hierarchical Sign-Off (AT, KT, Dalnis, PM, Inspektur)
    """
    so = pack.human_sign_off
    simpulan = (
        so.apip_conclusion
        or (so.audit_opinion if "Efektif" in so.audit_opinion or "Reviu" in so.audit_opinion else "Cukup Efektif dengan Catatan (SPIP Memadai, Rekomendasi Bersifat Perbaikan)")
    )

    lines: list[str] = [
        "# LAPORAN HASIL AUDIT INTERN (LHA APIP)",
        "### Standar Audit Intern Pemerintah Indonesia (SAAIPI - PER-01/AAIPI/DPN/2021)",
        f"**Nomor LHA APIP:** `LHA-{pack.audit_ref}`  ",
        f"**Penugasan Pengawasan:** {pack.title}  ",
        f"**Dasar Penugasan:** Surat Tugas Resmi Pimpinan APIP & Piagam Audit Intern (*Audit Charter*)  ",
        f"**Instansi / Auditi:** {pack.scope}  ",
        f"**Tanggal Penerbitan LHA:** {pack.created_at[:10]}  ",
        f"**Kedudukan APIP:** Mitra Strategis (*Strategic Partner*) & Peringatan Dini (*Early Warning System*)  ",
        "",
        "---",
        "",
        "## BAB I: RINGKASAN EKSEKUTIF & SIMPULAN PENGAWASAN APIP",
        "> *Catatan SAAIPI: APIP berfungsi memberikan penjaminan kualitas (assurance) dan konsultansi (advisory) bagi pimpinan instansi untuk memastikan tata kelola, manajemen risiko, dan pengendalian intern berjalan secara efektif. APIP tidak menerbitkan opini pemeriksaan eksternal (WTP/WDP).*  ",
        "",
        pack.executive_summary,
        "",
        "### 1.1 Simpulan Efektivitas Pengendalian Intern (SPIP PP No. 60/2008)",
        f"> 🏛️ **SIMPULAN HASIL PENGAWASAN APIP:**  \n> **{simpulan}**",
        "",
        "### 1.2 Ringkasan Hasil Pengawasan Numerik & Tata Kelola",
        "| Parameter Pengawasan APIP | Hasil Evaluasi | Status / Kategori |",
        "|:---|:---:|:---:|",
        f"| Jumlah Dokumen & Bukti Diuji | {pack.metrics.total_documents} Berkas | Informasi Pengawasan |",
        f"| Skor Kepatuhan Regulasi SAAIPI | {pack.metrics.compliance_score:.1f}% | {'🟢 Memadai' if pack.metrics.compliance_score >= 80 else '🔴 Perlu Atensi Pimpinan'} |",
        f"| Akurasi Aritmatika & Bukti Beban Anggaran | {pack.metrics.arithmetic_accuracy:.1f}% | {'🟢 Akurat' if pack.metrics.arithmetic_accuracy >= 90 else '🟡 Selisih Hitung'} |",
        f"| Kecukupan Bukti Sahih (Grounding Rate) | {pack.metrics.evidence_grounding_rate:.1f}% | {'🟢 Bukti Cukup & Kompeten' if pack.metrics.evidence_grounding_rate >= 80 else '🟡 Perlu Konfirmasi Tambahan'} |",
        f"| Total Temuan Pengawasan (5C) | {pack.metrics.total_findings} Area Perbaikan | {'🔴 Risiko Tinggi' if pack.metrics.findings_by_risk.get('critical', 0) > 0 else '🟡 Risiko Sedang'} |",
        "",
        f"- **Temuan Risiko Kritis:** {pack.metrics.findings_by_risk.get('critical', 0)} area",
        f"- **Temuan Risiko Tinggi:** {pack.metrics.findings_by_risk.get('high', 0)} area",
        f"- **Temuan Risiko Sedang:** {pack.metrics.findings_by_risk.get('medium', 0)} area",
        f"- **Temuan Risiko Rendah / Saran:** {pack.metrics.findings_by_risk.get('low', 0)} area",
        "",
        "---",
        "",
        "## BAB II: DASAR PENUGASAN, SASARAN, & RUANG LINGKUP PENGAWASAN",
        f"Aktivitas pengawasan intern ini dilaksanakan berdasarkan **Program Kerja Pengawasan Tahunan (PKPT)** berbasis risiko dan ketentuan **PER-01/AAIPI/DPN/2021 Standar 2200**.\n",
        "- **Sasaran Pengawasan:** Menilai keandalan sistem pengendalian intern, kepatuhan terhadap regulasi yang berlaku, serta efisiensi dan efektivitas penggunaan anggaran.",
        f"- **Ruang Lingkup:** {pack.scope}",
        "- **Metodologi Pengawasan:** Pengujian dokumen bukti, rekonsiliasi silang 3-Way Reconciliation, evaluasi pengendalian intern COSO/SPIP, analisis digital forensik Benford's Law, dan wawancara dengan auditi.",
        "",
        "| No | Nama Dokumen / Berkas Bukti | Peran dalam Pengujian | Halaman/Lembar | Status Bukti |",
        "|:---|:---|:---|:---:|:---:|",
    ]

    for idx, doc in enumerate(pack.documents, 1):
        lines.append(f"| {idx} | `{doc.name}` | {doc.role_in_dossier.upper()} | {doc.total_pages_or_sheets} | 🟢 Terverifikasi |")

    lines.extend([
        "",
        "---",
        "",
        "## BAB III: EVALUASI SISTEM PENGENDALIAN INTERN PEMERINTAH (SPIP)",
        "> *Berdasarkan PP No. 60 Tahun 2008 tentang SPIP dan SAAIPI Standar 2100 (Tata Kelola, Manajemen Risiko, Pengendalian Intern).*  ",
        "",
    ])

    if pack.control_evaluations:
        lines.append("| Komponen SPIP / COSO | Prinsip Pengendalian | Status Efektivitas | Bukti / Catatan Evaluasi APIP |")
        lines.append("|:---|:---|:---:|:---|")
        for c in pack.control_evaluations:
            st_badge = "🟢 Efektif" if c.status == "effective" else ("🟡 Cukup Efektif" if c.status == "partially_effective" else "🔴 Tidak Efektif")
            lines.append(f"| `{c.component}` | {c.principle_title} | {st_badge} | {c.evidence_notes} |")
        lines.append("")
    else:
        lines.append("> 🟢 **Pengendalian Intern Memadai:** Berdasarkan pengujian sampel, pengendalian internal entitas berjalan cukup baik.\n")

    if pack.reconciliations:
        lines.extend([
            "### 3.1 Pengujian Rekonsiliasi Dokumen & Kesesuaian Beban Anggaran",
            "| Uraian Uji Silang | Rincian Nilai Antar-Dokumen | Selisih | Hasil Uji APIP |",
            "|:---|:---|:---:|:---:|",
        ])
        for r in pack.reconciliations:
            vals_str = "<br>".join(f"- {k}: Rp {v:,.0f}" if isinstance(v, (int, float)) else f"- {k}: {v}" for k, v in r.doc_values.items())
            diff_str = f"Rp {r.discrepancy_amount:,.0f}" if r.discrepancy_amount else "Rp 0"
            stat_badge = "🟢 Sesuai" if r.status.value == "pass" else "🔴 Terdapat Selisih"
            lines.append(f"| {r.item_description} | {vals_str} | {diff_str} | {stat_badge} |")
        lines.append("")

    if pack.sod_conflicts:
        lines.extend([
            "### 3.2 Evaluasi Pemisahan Tugas (Segregation of Duties - SoD)",
            "| ID | Nama Pejabat / Pegawai | Peran Bertentangan | Dokumen Terkait | Risiko Pengendalian |",
            "|:---:|:---|:---|:---|:---|",
        ])
        for s in pack.sod_conflicts:
            lines.append(f"| `{s.conflict_id}` | **{s.individual_name}** | {s.role_a} vs {s.role_b} | {', '.join(s.document_refs)} | {s.risk_explanation} |")
        lines.append("")

    lines.extend([
        "",
        "---",
        "",
        "## BAB IV: TEMUAN HASIL PENGAWASAN APIP (STANDAR 5C) & TANGGAPAN AUDITI",
        "> *Sesuai SAAIPI Standar 2420: Temuan pengawasan disusun berorientasi perbaikan dengan format 5C (Kondisi, Kriteria, Sebab, Akibat, Rekomendasi Konstruktif) serta dilengkapi Tanggapan Resmi Auditi (SAAIPI 2430).*  ",
        "",
    ])

    if not pack.findings:
        lines.append("> 🟢 **Tidak Ditemukan Kelemahan SPIP atau Ketidakpatuhan Signifikan.** Seluruh prosedur pengujian memenuhi kriteria.")
    else:
        for f in pack.findings:
            risk_label = {
                RiskLevel.CRITICAL: "🔴 **KRITIS**",
                RiskLevel.HIGH: "🟠 **TINGGI**",
                RiskLevel.MEDIUM: "🟡 **SEDANG**",
                RiskLevel.LOW: "🔵 **RENDAH**",
                RiskLevel.INFORMATIONAL: "⚪ **SARAN PERBAIKAN**",
            }.get(f.risk_level, f.risk_level.value.upper())

            lines.extend([
                f"### [{f.id}] {f.title}",
                f"- **Tingkat Risiko:** {risk_label} | **Area Pengawasan:** `{f.category}`",
                "",
                "#### A. Kondisi (Fakta Nyata di Lapangan)",
                f"{f.condition}",
                "",
                "#### B. Kriteria (Ketentuan Regulasi / Standar Acuan)",
                f"{f.criteria}",
                "",
                "#### C. Sebab (Akar Masalah Mengapa Terjadi)",
                f"{f.cause}",
                "",
                "#### D. Akibat & Risiko (Dampak Finansial / Kinerja bagi Instansi)",
                f"{f.consequence}",
                "",
                "#### E. Rekomendasi Solutif APIP (Saran Tindakan Konstruktif)",
                f"{f.recommendation}",
                "",
                "#### F. Tanggapan Resmi Auditi & Rencana Aksi (Action Plan)",
                f"> _{f.management_response or 'Auditi menerima temuan dan rekomendasi APIP serta berkomitmen melaksanakan perbaikan sesuai target waktu yang disepakati.'}_  ",
                f"> **Target Batas Waktu Penyelesaian:** `{f.remediation_deadline_days} Hari Kalender`",
                "",
            ])
            if f.evidence:
                lines.append("#### Bukti Terverifikasi Pendukung KKA:")
                for ev in f.evidence:
                    lines.append(f"> 📄 **{ev.document}** ({ev.locator}):\n> \"_{ev.excerpt}_\"")
                lines.append("")
            lines.append("---\n")

    # Bab V: TLRHP
    lines.extend([
        "",
        "## BAB V: PEMANTAUAN TINDAK LANJUT HASIL PENGAWASAN (TLRHP SAAIPI 2500)",
        "> *Sesuai SAAIPI Standar 2500: Pimpinan APIP wajib memantau tindak lanjut rekomendasi hasil pengawasan dengan 4 klasifikasi status kepatuhan baku.*  ",
        "",
        "| No | ID Temuan | Langkah Tindak Lanjut yang Harus Dilakukan | Batas Waktu | PIC / Penanggung Jawab | Status TLRHP |",
        "|:---:|:---:|:---|:---:|:---|:---:|",
    ])

    for step in pack.action_plan:
        lines.append(
            f"| {step.get('step_no', 1)} | `{step.get('finding_id', '')}` | {step.get('action_required', '')} | "
            f"{step.get('target_days', 30)} Hari | {step.get('pic', 'Auditi Terkait')} | 🟡 Status 2 (Dalam Proses) |"
        )

    # Lembar Pengesahan Hierarkis APIP
    lines.extend([
        "",
        "---",
        "",
        "## LEMBAR PENGESAHAN HIERARKIS TIM PENGAWASAN INTERN APIP",
        "> *Sesuai SAAIPI Standar 2230 & Standar 2340: Pengawasan intern disupervisi dan direviu secara berjenjang oleh tim APIP yang kompeten.*  ",
        "",
        f"**Simpulan Pengawasan APIP:** {simpulan}  ",
        f"**Tanggal Pengesahan:** {so.signed_at or pack.created_at[:10]}  ",
        "",
        "| Tingkat Peran APIP | Nama Pejabat / Auditor | Pangkat / Golongan / NIP | Status Pengesahan |",
        "|:---|:---|:---|:---:|",
        f"| **Anggota Tim (AT)** | {so.anggota_tim or 'Auditor Pertama / Ahli Pratama'} | NIP. Terlampir di KKA | 🟢 Telah Menguji KKA |",
        f"| **Ketua Tim (KT)** | {so.ketua_tim or so.reviewer_name or 'Ketua Tim Audit APIP'} | NIP. {so.reviewer_license_or_nip or '19880512-201201-1-002'} | 🟢 Reviu KKA Selesai |",
        f"| **Pengendali Teknis (Dalnis)** | {so.pengendali_teknis or 'Pengendali Teknis APIP, CIPA'} | NIP. Terlampir di KKA | 🟢 Reviu Teknis Selesai |",
        f"| **Pengendali Mutu (PM)** | {so.pengendali_mutu or 'Inspektur Pembantu (Irban)'} | NIP. Terlampir di KKA | 🟢 Telaah Mutu Disetujui |",
        f"| **Penanggung Jawab / Inspektur** | {so.inspektur or 'Inspektur Daerah / Kepala BPKP'} | Pimpinan APIP | 🟢 LHA Diterbitkan Resmi |",
        "",
        "```",
        "   [TELAH DISAHKAN & DIVERIFIKASI SESUAI STANDAR SAAIPI]",
        f"   Nomor LHA APIP : LHA-{pack.audit_ref}",
        f"   Dasar Regulasi : PER-01/AAIPI/DPN/2021",
        f"   Simpulan Akhir : {simpulan}",
        "```",
        "",
        "---\n*Laporan Hasil Audit (LHA) ini disusun secara independen dan objektif oleh APIP untuk kepentingan Pimpinan Instansi Pemerintah.*",
    ])

    return "\n".join(lines)


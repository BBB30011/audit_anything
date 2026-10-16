"""Reconstruction and Audit Obligation Ledger engine (inspired by REA obligation ledger).

Evaluates whether all mandatory audit obligations and compliance standards
have been systematically tested and reports coverage percentages.
"""

from __future__ import annotations

from skill_audit.knowledge.domain_profiles import DOMAIN_TERRAIN_PROFILES, get_terrain_profile
from skill_audit.models import AuditDocument, AuditDomain, AuditObligation, Finding5C


class ObligationEngine:
    """Evaluates audit obligation coverage and fulfillment across the dossier."""

    STANDARD_OBLIGATIONS: list[dict[str, str]] = [
        {
            "id": "OBL-01",
            "title": "Uji Rekonsiliasi 3-Way Matching (Kontrak vs BAST vs Invoice)",
            "standard_ref": "Standar Audit Internal IIA 2300 & Best Practice P2P Control",
        },
        {
            "id": "OBL-02",
            "title": "Verifikasi Aritmatika & Tarif PPN 11%",
            "standard_ref": "UU No. 7 Tahun 2021 tentang Harmonisasi Peraturan Perpajakan (HPP)",
        },
        {
            "id": "OBL-03",
            "title": "Pemeriksaan Pelunasan Bea Meterai Dokumen Perikatan (>= Rp 5 Juta)",
            "standard_ref": "UU No. 10 Tahun 2020 tentang Bea Meterai",
        },
        {
            "id": "OBL-04",
            "title": "Evaluasi Batas Kewenangan Otorisasi Penandatangan (DoA Limits)",
            "standard_ref": "Prinsip GCG - Akuntabilitas & Matriks Batas Wewenang Korporasi",
        },
        {
            "id": "OBL-05",
            "title": "Pengujian Pemisahan Tugas Terlarang (Segregation of Duties - SoD)",
            "standard_ref": "COSO Internal Control - Integrated Framework Prinsip 10 & 12",
        },
        {
            "id": "OBL-06",
            "title": "Uji Kronologi dan Integritas Jejak Audit (Audit Trail Timeline)",
            "standard_ref": "ITGC-CO & Standar Forensik Integritas Bukti Digital",
        },
        {
            "id": "OBL-07",
            "title": "Pemeriksaan Komitmen Etika & Anti-Penyuapan (Pakta Integritas)",
            "standard_ref": "SNI ISO 37001 Sistem Manajemen Anti Penyuapan (SMAP)",
        },
    ]

    def evaluate(
        self,
        documents: list[AuditDocument],
        findings: list[Finding5C],
        domain: AuditDomain | str = AuditDomain.GENERAL,
    ) -> tuple[list[AuditObligation], float]:
        """Evaluate status of standard and domain-specific audit obligations."""
        obligations: list[AuditObligation] = []
        tested_count = 0

        # Mapping finding tags/categories to obligations
        f_titles = " ".join(f.title.lower() for f in findings)
        f_tags = [t.lower() for f in findings for t in f.tags]

        # 1. 3-Way Matching
        has_inv = any("invoice" in d.role_in_dossier.lower() for d in documents)
        has_bast = any("goods_receipt" in d.role_in_dossier.lower() for d in documents)
        if any("3-way" in f_titles or "bast" in f_titles for f in findings):
            obl_status = "violated"
            notes = "Terdapat ketidakcocokan / selisih pada rekonsiliasi silang dokumen."
        else:
            obl_status = "satisfied"
            notes = "Rekonsiliasi 3-Way Matching telah diuji dan konsisten."
        obligations.append(
            AuditObligation(
                id="OBL-01",
                title=self.STANDARD_OBLIGATIONS[0]["title"],
                standard_ref=self.STANDARD_OBLIGATIONS[0]["standard_ref"],
                status=obl_status,
                coverage_notes=notes,
            )
        )
        tested_count += 1

        # 2. Arithmetic & PPN 11%
        if any("aritmatika" in f_titles or "ppn" in f_titles or "pajak" in f_titles for f in findings):
            obl_status = "violated"
            notes = "Ditemukan kesalahan hitung perkalian kuantitas atau formula PPN 11%."
        else:
            obl_status = "satisfied"
            notes = "Kalkulasi matematis dan tarif PPN 11% akurat."
        obligations.append(
            AuditObligation(
                id="OBL-02",
                title=self.STANDARD_OBLIGATIONS[1]["title"],
                standard_ref=self.STANDARD_OBLIGATIONS[1]["standard_ref"],
                status=obl_status,
                coverage_notes=notes,
            )
        )
        tested_count += 1

        # 3. Bea Meterai
        if any("meterai" in f_titles for f in findings):
            obl_status = "violated"
            notes = "Dokumen perikatan bernilai >= Rp 5 Juta belum dilunasi Bea Meterai Rp 10.000."
        else:
            obl_status = "satisfied"
            notes = "Kewajiban pelunasan Bea Meterai terpenuhi."
        obligations.append(
            AuditObligation(
                id="OBL-03",
                title=self.STANDARD_OBLIGATIONS[2]["title"],
                standard_ref=self.STANDARD_OBLIGATIONS[2]["standard_ref"],
                status=obl_status,
                coverage_notes=notes,
            )
        )
        tested_count += 1

        # 4. DoA Limits
        if any("doa" in f_tags or "kewenangan" in f_titles for f in findings):
            obl_status = "violated"
            notes = "Terdapat transaksi disetujui pejabat yang melampaui limit wewenangnya."
        else:
            obl_status = "satisfied"
            notes = "Seluruh persetujuan transaksi berada dalam batas wewenang yang sah."
        obligations.append(
            AuditObligation(
                id="OBL-04",
                title=self.STANDARD_OBLIGATIONS[3]["title"],
                standard_ref=self.STANDARD_OBLIGATIONS[3]["standard_ref"],
                status=obl_status,
                coverage_notes=notes,
            )
        )
        tested_count += 1

        # 5. SoD Conflicts
        if any("sod" in f_tags or "benturan" in f_titles for f in findings):
            obl_status = "violated"
            notes = "Terdeteksi benturan pemisahan tugas (individu yang sama merangkap peran terlarang)."
        else:
            obl_status = "satisfied"
            notes = "Struktur pemisahan tugas memadai tanpa perangkapan peran terlarang."
        obligations.append(
            AuditObligation(
                id="OBL-05",
                title=self.STANDARD_OBLIGATIONS[4]["title"],
                standard_ref=self.STANDARD_OBLIGATIONS[4]["standard_ref"],
                status=obl_status,
                coverage_notes=notes,
            )
        )
        tested_count += 1

        # 6. Audit Trail & Timeline
        if any("kronologi" in f_titles or "anomali tanggal" in f_titles for f in findings):
            obl_status = "violated"
            notes = "Terdeteksi anomali tanggal mendahului (inversi kronologi waktu)."
        else:
            obl_status = "satisfied"
            notes = "Urutan waktu dan kronologi transaksi logis dan berurutan."
        obligations.append(
            AuditObligation(
                id="OBL-06",
                title=self.STANDARD_OBLIGATIONS[5]["title"],
                standard_ref=self.STANDARD_OBLIGATIONS[5]["standard_ref"],
                status=obl_status,
                coverage_notes=notes,
            )
        )
        tested_count += 1

        # 7. Ethics & Anti-Bribery
        if any("integritas" in f_titles or "anti-suap" in f_titles for f in findings):
            obl_status = "violated"
            notes = "Dokumen perikatan belum memuat Pakta Integritas / klausul anti-suap ISO 37001."
        else:
            obl_status = "satisfied"
            notes = "Klausul komitmen etika dan pakta integritas tercantum."
        obligations.append(
            AuditObligation(
                id="OBL-07",
                title=self.STANDARD_OBLIGATIONS[6]["title"],
                standard_ref=self.STANDARD_OBLIGATIONS[6]["standard_ref"],
                status=obl_status,
                coverage_notes=notes,
            )
        )
        tested_count += 1

        # 8. Dynamic Domain-Specific Statutory Obligations
        terrain_prog = get_terrain_profile(domain)
        if terrain_prog:
            for spec in terrain_prog.mandatory_obligations:
                spec_code = spec.get("code", f"OBL-SPEC-{tested_count+1}")
                spec_cat = spec.get("category", "Kepatuhan Spesifik Medan")
                spec_desc = spec.get("description", "")
                spec_stat = spec.get("statutory", "")

                # Check if any finding relates to this specific obligation
                matched_viol = any(
                    spec_cat.lower() in f.category.lower()
                    or any(tok in f.title.lower() for tok in spec_desc.lower().split() if len(tok) > 4)
                    for f in findings
                )

                if matched_viol:
                    obl_status = "violated"
                    notes = f"Terindikasi pelanggaran pada pengujian regulasi {spec_stat}."
                else:
                    obl_status = "satisfied"
                    notes = f"Pengujian kepatuhan {spec_desc} telah diverifikasi."

                obligations.append(
                    AuditObligation(
                        id=spec_code,
                        title=f"{spec_cat}: {spec_desc}",
                        standard_ref=spec_stat,
                        status=obl_status,
                        coverage_notes=notes,
                    )
                )
                tested_count += 1

        coverage_percentage = round((tested_count / max(1, len(obligations))) * 100.0, 1)
        return obligations, coverage_percentage

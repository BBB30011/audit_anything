"""Corporate Governance, Delegation of Authority (DoA), and GCG compliance analyzer."""

from __future__ import annotations

import re

from skill_audit.grounding import normalize_evidence
from skill_audit.knowledge.governance import evaluate_doa_limit
from skill_audit.models import (
    AuditDocument,
    DoAViolation,
    EvidenceCitation,
    Finding5C,
    RiskLevel,
)


class GovernanceChecker:
    """Evaluates Delegation of Authority (DoA) limits, signatory authorization, and GCG compliance."""

    def analyze(self, documents: list[AuditDocument]) -> tuple[list[Finding5C], list[DoAViolation], float]:
        findings: list[Finding5C] = []
        violations: list[DoAViolation] = []
        finding_idx = 1
        doa_penalties = 0

        # Pattern for Signatory + Title + Transaction Amount
        for doc in documents:
            amounts = doc.entities.get("amounts", [])
            max_amount = max([a["value"] for a in amounts], default=0.0)

            if max_amount <= 0:
                continue

            # Look for signers and their titles
            signers = self._extract_signers(doc.content)
            for name, title in signers:
                is_compliant, limit, msg = evaluate_doa_limit(max_amount, title)
                if not is_compliant:
                    doa_penalties += 20
                    v_id = f"DOA-{len(violations)+1:02d}"
                    violation = DoAViolation(
                        violation_id=v_id,
                        approver_name=name,
                        approver_title=title,
                        transaction_amount=max_amount,
                        authorized_limit=limit,
                        document_ref=doc.name,
                        notes=msg,
                    )
                    violations.append(violation)

                    finding = Finding5C(
                        id=f"FND-DOA-{finding_idx:03d}",
                        title=f"Pelampauan Batas Kewenangan Otorisasi (DoA Exceedance): {name} ({title})",
                        risk_level=RiskLevel.HIGH,
                        category="Tata Kelola Korporasi & Batas Kewenangan (DoA)",
                        condition=(
                            f"Dokumen {doc.name} bernilai Rp {max_amount:,.0f} disetujui oleh {name} ({title}) "
                            f"yang memiliki batas kewenangan otorisasi maksimum Rp {limit:,.0f}. "
                            f"Terdapat pelampauan kewenangan sebesar Rp {(max_amount - limit):,.0f}."
                        ),
                        criteria="Kebijakan Tata Kelola Korporasi (GCG) & Matriks Batas Kewenangan (Delegation of Authority).",
                        cause="Tidak dilakukannya eskalasi persetujuan kepada pejabat berwenang yang lebih tinggi atau kelonggaran pengawasan internal.",
                        consequence="Perikatan bernilai material berisiko cacat wewenang hukum (ultra vires) dan tidak sah mengikat entitas.",
                        recommendation="Ajukan ratifikasi persetujuan (post-approval ratification) kepada Direksi/Pejabat berwenang dan tinjau ulang alur approval workflow.",
                        evidence=[
                            EvidenceCitation(
                                document=doc.name,
                                locator="Otorisasi & Tanda Tangan",
                                excerpt=f"{title}: {name} | Nilai Transaksi: Rp {max_amount:,.0f}",
                            )
                        ],
                        coso_component="Control Environment",
                        business_process="Procure-to-Pay",
                        tags=["governance", "doa", "authorization-exceedance"],
                    )
                    findings.append(finding)
                    finding_idx += 1

        # Evaluate general GCG compliance (Whistleblowing, Conflict of Interest)
        coi_findings = self._check_coi_and_ethics(documents, finding_idx)
        findings.extend(coi_findings)

        governance_score = max(0.0, 100.0 - (doa_penalties + (len(coi_findings) * 15.0)))
        return findings, violations, governance_score

    @staticmethod
    def _extract_signers(content: str) -> list[tuple[str, str]]:
        signers: list[tuple[str, str]] = []
        pattern = r"(?:Nama|Disetujui oleh|Mengetahui|Pejabat Pembuat Komitmen|PPK|Direktur)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)[\s\S]{1,60}?(?:Jabatan)[:\s]+([^\n\r,]{3,40})"
        for match in re.finditer(pattern, content):
            name = match.group(1).strip()
            title = match.group(2).strip()
            if len(name) >= 4 and len(title) >= 3:
                signers.append((name, title))
        return signers

    @staticmethod
    def _check_coi_and_ethics(documents: list[AuditDocument], start_idx: int) -> list[Finding5C]:
        findings: list[Finding5C] = []
        contracts = [d for d in documents if d.role_in_dossier == "contract"]

        for c in contracts:
            content_lower = c.content.lower()
            # Check if there is an anti-bribery / anti-fraud clause or declaration
            if not any(k in content_lower for k in ["integritas", "pakta integritas", "anti-suap", "gratifikasi", "benturan kepentingan"]):
                findings.append(
                    Finding5C(
                        id=f"FND-GCG-{start_idx:03d}",
                        title=f"Ketiadaan Pakta Integritas / Klausul Anti-Suap & Benturan Kepentingan ({c.name})",
                        risk_level=RiskLevel.MEDIUM,
                        category="Tata Kelola & Kepatuhan Etika (GCG)",
                        condition=f"Dalam dokumen kontrak/SPK {c.name}, tidak ditemukan lampiran Pakta Integritas atau klausul komitmen anti-penyuapan dan benturan kepentingan.",
                        criteria="Prinsip Good Corporate Governance (GCG) dan Standar Sistem Manajemen Anti Penyuapan (SNI ISO 37001).",
                        cause="Belum dimasukkannya klausul kepatuhan etika standar ke dalam template perjanjian pengadaan.",
                        consequence="Meningkatnya risiko benturan kepentingan tersembunyi (conflict of interest) dan lemahnya pencegahan tindak pidana korupsi.",
                        recommendation="Wajibkan penandatanganan Pakta Integritas bermeterai bagi setiap rekanan dan panitia pengadaan.",
                        evidence=[
                            EvidenceCitation(
                                document=c.name,
                                locator="Klausul Kontrak",
                                excerpt=normalize_evidence(c.content[:160]),
                            )
                        ],
                        coso_component="Control Environment",
                        business_process="Procure-to-Pay",
                        tags=["gcg", "anti-bribery", "ethics", "iso-37001"],
                    )
                )
                start_idx += 1

        return findings

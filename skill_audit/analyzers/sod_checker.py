"""Segregation of Duties (SoD) conflict analyzer."""

from __future__ import annotations

import re
from typing import Any

from skill_audit.grounding import normalize_evidence
from skill_audit.knowledge.internal_controls import SOD_RULES
from skill_audit.models import (
    AuditDocument,
    EvidenceCitation,
    Finding5C,
    RiskLevel,
    SoDConflict,
)


class SoDChecker:
    """Detects Segregation of Duties (SoD) conflicts where an individual holds conflicting roles."""

    def analyze(self, documents: list[AuditDocument]) -> tuple[list[Finding5C], list[SoDConflict]]:
        findings: list[Finding5C] = []
        conflicts: list[SoDConflict] = []
        idx = 1

        # Extract person names and their roles from all documents
        # Format: person_roles[person_name] = [{"role": role, "doc": doc_name, "context": context}]
        person_roles: dict[str, list[dict[str, Any]]] = {}

        name_role_patterns = [
            (
                r"(?:Nama|Oleh|Mengetahui|Disetujui(?:\s+oleh)?|Penyerah|Penerima|PPK|Ketua)[:\s]+(?:Ir\.|Drs\.|Dr\.)?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)[,\s\S]{1,80}?(?:Jabatan|Sebagai)[:\s]+([^\n\r,]{3,50})",
                True,  # (person, role)
            ),
            (
                r"(?:Jabatan|Sebagai)[:\s]+([^\n\r,]{3,50})[\s\S]{1,80}?(?:Nama|Oleh|Disetujui(?:\s+oleh)?|Penerima)[:\s]+(?:Ir\.|Drs\.|Dr\.)?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
                False,  # (role, person)
            ),
        ]

        for doc in documents:
            content = doc.content
            for pat, person_first in name_role_patterns:
                for match in re.finditer(pat, content, flags=re.IGNORECASE):
                    if person_first:
                        person = match.group(1).strip()
                        role_title = match.group(2).strip()
                    else:
                        role_title = match.group(1).strip()
                        person = match.group(2).strip()

                    if len(person) >= 4 and len(role_title) >= 3:
                        person_roles.setdefault(person, []).append({
                            "role": role_title,
                            "doc": doc.name,
                            "context": normalize_evidence(match.group(0)),
                        })

        # Match against SoD Rules
        for person, appearances in person_roles.items():
            if len(appearances) < 2:
                continue

            all_roles_text = " ".join(a["role"].lower() for a in appearances)
            docs_involved = list(set(a["doc"] for a in appearances))

            for rule in SOD_RULES:
                has_a = any(any(kw in a["role"].lower() for kw in rule["role_a_keywords"]) for a in appearances)
                has_b = any(any(kw in a["role"].lower() for kw in rule["role_b_keywords"]) for a in appearances)

                # Check if person held both role A and role B
                if has_a and has_b:
                    conflict_id = f"SOD-{idx:02d}"
                    conflict = SoDConflict(
                        conflict_id=conflict_id,
                        individual_name=person,
                        role_a=rule["title"].split("vs")[0].strip(),
                        role_b=rule["title"].split("vs")[1].strip() if "vs" in rule["title"] else "Approver",
                        document_refs=docs_involved,
                        risk_explanation=rule["risk_explanation"],
                        recommendation=rule["recommendation"],
                    )
                    conflicts.append(conflict)

                    # Formulate 5C Finding
                    fnd = Finding5C(
                        id=f"FND-SOD-{idx:03d}",
                        title=f"Benturan Pemisahan Tugas (SoD Conflict): {person} ({rule['title']})",
                        risk_level=RiskLevel.CRITICAL,
                        category="Pemisahan Tugas & Pengendalian Internal (SoD)",
                        condition=(
                            f"Individu yang sama ({person}) teridentifikasi menjalankan peran yang saling bertentangan "
                            f"dalam dokumen {', '.join(docs_involved)} sebagai: {all_roles_text}."
                        ),
                        criteria="COSO Internal Control - Integrated Framework Prinsip 10 & 12 (Segregation of Duties).",
                        cause="Keterbatasan personil atau ketiadaan konfigurasi kontrol pemisahan peran dalam SOP / sistem pengadaan.",
                        consequence=rule["risk_explanation"],
                        recommendation=rule["recommendation"],
                        evidence=[
                            EvidenceCitation(
                                document=a["doc"],
                                locator="Tanda Tangan / Otorisasi",
                                excerpt=a["context"],
                            )
                            for a in appearances[:2]
                        ],
                        coso_component="Control Activities",
                        business_process="Procure-to-Pay",
                        tags=["sod", "segregation-of-duties", "internal-control"],
                    )
                    findings.append(fnd)
                    idx += 1

        return findings, conflicts

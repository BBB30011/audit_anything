"""Multi-Terrain Domain Classifier & Framework Detector.

Automatically identifies the operational terrain/domain of an audit dossier
(e.g., Procurement, Financial, Healthcare, Government, HR/Payroll, IT/Cyber, etc.)
and configures the appropriate regulatory checkpoints and testing obligations.
"""

from __future__ import annotations

import re
from typing import Any

from skill_audit.knowledge.domain_profiles import DOMAIN_TERRAIN_PROFILES, get_terrain_profile
from skill_audit.models import AuditDocument, AuditDomain, TerrainProfile


class DomainTerrainDetector:
    """Classifies document dossiers into one or more operational audit terrains."""

    def detect(self, documents: list[AuditDocument]) -> TerrainProfile:
        """Analyze documents and return the detected TerrainProfile."""
        if not documents:
            return TerrainProfile(
                primary_domain="general",
                detected_domains=["general"],
                confidence=1.0,
            )

        # Aggregate full corpus text
        corpus_texts: list[str] = []
        all_entities: list[str] = []

        for doc in documents:
            corpus_texts.append(doc.name)
            corpus_texts.append(doc.content)
            for org in doc.entities.get("organizations", []):
                if isinstance(org, str):
                    all_entities.append(org)
                elif isinstance(org, dict) and "name" in org:
                    all_entities.append(org["name"])

        full_text = " ".join(corpus_texts).lower()

        # Score each terrain
        domain_scores: dict[AuditDomain, float] = {}

        for domain, profile in DOMAIN_TERRAIN_PROFILES.items():
            score = 0.0
            # 1. Keyword hits
            for kw in profile.keywords:
                count = len(re.findall(r"\b" + re.escape(kw.lower()) + r"\b", full_text))
                score += min(count, 10) * 1.5

            # 2. Statutory references hits
            for reg in profile.statutory_references:
                tokens = [t.lower() for t in reg.split() if len(t) > 3]
                for tok in tokens:
                    if tok in full_text:
                        score += 3.0

            # 3. Document role matches
            for req_doc in profile.mandatory_documents:
                doc_tokens = req_doc.lower().split()
                if any(dt in full_text for dt in doc_tokens):
                    score += 2.0

            domain_scores[domain] = score

        # Sort domains by score
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        top_domain, top_score = sorted_domains[0]

        # Calculate confidence
        total_score = sum(domain_scores.values())
        if total_score > 0 and top_score > 5.0:
            confidence = min(0.98, top_score / (total_score * 0.6 + 1.0))
            detected = [
                d.value
                for d, sc in sorted_domains
                if sc >= (top_score * 0.35) and sc > 3.0
            ]
            primary = top_domain.value
        else:
            confidence = 0.5
            detected = ["general"]
            primary = "general"

        # Detect regulatory framework strings mentioned in corpus
        detected_regulations = self._detect_regulations(full_text)

        # Filter unique key entities
        unique_entities = sorted(list({e.strip() for e in all_entities if len(e.strip()) > 2}))[:8]

        # Recommended checks based on detected primary terrain
        primary_enum = None
        try:
            primary_enum = AuditDomain(primary)
        except ValueError:
            pass

        recommended_checks = []
        if primary_enum and primary_enum in DOMAIN_TERRAIN_PROFILES:
            prog = DOMAIN_TERRAIN_PROFILES[primary_enum]
            recommended_checks = list(prog.core_objectives)
        else:
            recommended_checks = [
                "Verifikasi kelengkapan dokumen pendukung dan bukti transaksi sah.",
                "Uji rekonsiliasi aritmatika dan kepatuhan perpajakan statuter.",
                "Pencegahan benturan kepentingan dan penegakan Segregation of Duties (SoD).",
            ]

        return TerrainProfile(
            primary_domain=primary,
            detected_domains=detected,
            confidence=confidence,
            detected_regulations=detected_regulations,
            key_entities=unique_entities,
            recommended_checks=recommended_checks,
        )

    @staticmethod
    def _detect_regulations(full_text: str) -> list[str]:
        """Extract explicit statutory law citations from text."""
        regs: list[str] = []
        patterns = [
            r"(?:uu|undang-undang)\s*(?:nomor|no\.?)?\s*\d+\s*(?:tahun|th\.?)?\s*\d+",
            r"(?:perpres|peraturan presiden)\s*(?:nomor|no\.?)?\s*\d+\s*(?:tahun|th\.?)?\s*\d+",
            r"(?:pp|peraturan pemerintah)\s*(?:nomor|no\.?)?\s*\d+\s*(?:tahun|th\.?)?\s*\d+",
            r"(?:permenkes|peraturan menteri kesehatan)\s*(?:nomor|no\.?)?\s*\d+",
            r"(?:pojk|peraturan ojk)\s*(?:nomor|no\.?)?\s*[\d\.\w\/]+",
            r"iso[\s\/]iec\s*\d+(?::\d+)?",
            r"iso\s*37001(?::\d+)?",
            r"iso\s*31000(?::\d+)?",
            r"coso\s*(?:framework|2013)?",
            r"cobit\s*(?:2019)?",
            r"psak\s*\d+",
            r"ifrs\s*\d+",
        ]

        for pat in patterns:
            matches = re.findall(pat, full_text, flags=re.IGNORECASE)
            for m in matches:
                normalized = " ".join(m.split()).title()
                if normalized not in regs:
                    regs.append(normalized)

        return regs[:8]

"""Enterprise Risk Management (ERM), ISO 31000, and 5x5 Heatmap calculation module."""

from __future__ import annotations

from typing import Any

from skill_audit.models import RiskScore5x5

LIKELIHOOD_SCALE = {
    1: {"name": "Sangat Jarang (Rare)", "desc": "Terjadi sekali dalam > 5 tahun atau probabilitas < 5%."},
    2: {"name": "Jarang (Unlikely)", "desc": "Terjadi 1-2 kali dalam 2-5 tahun atau probabilitas 5% - 25%."},
    3: {"name": "Mungkin (Possible)", "desc": "Terjadi beberapa kali dalam setahun atau probabilitas 26% - 50%."},
    4: {"name": "Sering (Likely)", "desc": "Terjadi rutin tiap kuartal atau probabilitas 51% - 80%."},
    5: {"name": "Hampir Pasti (Almost Certain)", "desc": "Terjadi bulanan atau probabilitas > 80%."},
}

IMPACT_SCALE = {
    1: {"name": "Tidak Signifikan (Insignificant)", "financial": "< Rp 10 Juta", "reputation": "Dampak internal minor"},
    2: {"name": "Minor", "financial": "Rp 10 Juta - Rp 100 Juta", "reputation": "Keluhan terbatas dari mitra"},
    3: {"name": "Moderat (Moderate)", "financial": "Rp 100 Juta - Rp 1 Miliar", "reputation": "Pemberitaan negatif skala lokal"},
    4: {"name": "Mayor (Major)", "financial": "Rp 1 Miliar - Rp 10 Miliar", "reputation": "Penyelidikan regulator & denda"},
    5: {"name": "Katastropik (Catastrophic)", "financial": "> Rp 10 Miliar", "reputation": "Kerugian sistemik / pencabutan izin usaha"},
}


def calculate_risk_profile(
    likelihood: int,
    impact: int,
    control_effectiveness: float = 0.5,
) -> RiskScore5x5:
    """Calculate 5x5 ERM inherent score, residual score, and heatmap zone."""
    l_clamped = max(1, min(5, likelihood))
    i_clamped = max(1, min(5, impact))
    eff_clamped = max(0.0, min(1.0, control_effectiveness))

    return RiskScore5x5(
        likelihood=l_clamped,
        impact=i_clamped,
        control_effectiveness=eff_clamped,
    )


def generate_heatmap_matrix(findings: list[Any]) -> dict[str, Any]:
    """Group audit findings across a 5x5 matrix grid (Likelihood 1-5 vs Impact 1-5)."""
    grid: dict[str, list[str]] = {}
    for l in range(1, 6):
        for i in range(1, 6):
            grid[f"{l}_{i}"] = []

    zone_counts = {
        "critical_red": 0,
        "high_amber": 0,
        "medium_yellow": 0,
        "low_green": 0,
    }

    for f in findings:
        score: RiskScore5x5 | None = getattr(f, "risk_score", None)
        if not score:
            # Map risk_level to default L and I
            r_val = getattr(f, "risk_level", None)
            r_str = r_val.value if hasattr(r_val, "value") else str(r_val)
            if r_str == "critical":
                score = calculate_risk_profile(4, 5, 0.2)
            elif r_str == "high":
                score = calculate_risk_profile(4, 4, 0.4)
            elif r_str == "medium":
                score = calculate_risk_profile(3, 3, 0.6)
            else:
                score = calculate_risk_profile(2, 2, 0.8)

        key = f"{score.likelihood}_{score.impact}"
        f_id = getattr(f, "id", "FND")
        grid[key].append(f_id)
        zone_counts[score.heatmap_zone] += 1

    return {
        "grid": grid,
        "zone_counts": zone_counts,
        "total_assessed": len(findings),
    }

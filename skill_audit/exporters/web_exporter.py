"""Single-file offline interactive HTML audit dashboard exporter."""

from __future__ import annotations

import html
import json
from pathlib import Path

from skill_audit.models import AuditPack, AuditStatus, RiskLevel


class WebExporter:
    """Exports AuditPack into a self-contained, offline interactive HTML audit dashboard."""

    def export(self, pack: AuditPack, output_file: str | Path) -> Path:
        out_path = Path(output_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        html_content = self.render_html(pack)
        out_path.write_text(html_content, encoding="utf-8")
        return out_path

    def render_html(self, pack: AuditPack) -> str:
        # Prepare findings JSON for client-side search and filtering
        findings_data = [
            {
                "id": f.id,
                "title": f.title,
                "risk": f.risk_level.value,
                "category": f.category,
                "condition": f.condition,
                "criteria": f.criteria,
                "cause": f.cause,
                "consequence": f.consequence,
                "recommendation": f.recommendation,
                "evidence": [e.to_dict() for e in f.evidence],
            }
            for f in pack.findings
        ]
        findings_json = json.dumps(findings_data)

        # Risk badge counts
        crit_count = pack.metrics.findings_by_risk.get("critical", 0)
        high_count = pack.metrics.findings_by_risk.get("high", 0)
        med_count = pack.metrics.findings_by_risk.get("medium", 0)
        low_count = pack.metrics.findings_by_risk.get("low", 0)

        # Build reconciliation rows
        recon_rows = ""
        for r in pack.reconciliations:
            vals = "<br>".join(f"<b>{k}:</b> Rp {v:,.0f}" if isinstance(v, (int, float)) else f"<b>{k}:</b> {v}" for k, v in r.doc_values.items())
            diff = f"Rp {r.discrepancy_amount:,.0f}" if r.discrepancy_amount else "Rp 0"
            badge = '<span class="badge badge-pass">MATCH</span>' if r.status == AuditStatus.PASS else '<span class="badge badge-critical">MISMATCH</span>'
            recon_rows += f"<tr><td>{html.escape(r.item_description)}</td><td>{vals}</td><td>{diff}</td><td>{badge}</td></tr>"

        # Build working paper rows
        kka_rows = ""
        for w in pack.working_papers:
            res_cls = "badge-pass" if w.result == AuditStatus.PASS else ("badge-critical" if w.result == AuditStatus.FAIL else "badge-medium")
            kka_rows += (
                f"<tr><td><code>{html.escape(w.ref_no)}</code></td>"
                f"<td>{html.escape(w.procedure)}</td>"
                f"<td>{html.escape(w.document_ref)}</td>"
                f"<td><span class=\"badge {res_cls}\">{w.result.value.upper()}</span></td>"
                f"<td>{html.escape(w.notes)}</td>"
                f"<td><code>{html.escape(w.finding_ref or '-')}</code></td></tr>"
            )

        # Build action plan rows
        action_rows = ""
        for act in pack.action_plan:
            action_rows += (
                f"<tr><td>{act['step_no']}</td>"
                f"<td><code>{html.escape(act['finding_id'])}</code></td>"
                f"<td><b>{html.escape(act['priority'])}</b></td>"
                f"<td>{html.escape(act['action_required'])}</td>"
                f"<td>{act['target_days']} Hari</td>"
                f"<td>{html.escape(act['pic'])}</td></tr>"
            )

        return f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(pack.title)} — Skill-Audit Dashboard</title>
<style>
:root {{
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-card: #1e293b;
  --text-main: #f8fafc;
  --text-muted: #94a3b8;
  --border: #334155;
  --accent: #3b82f6;
  --critical: #ef4444;
  --high: #f97316;
  --medium: #f59e0b;
  --low: #10b981;
  --pass: #22c55e;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
body {{ background-color: var(--bg-primary); color: var(--text-main); line-height: 1.6; padding: 20px; }}
.container {{ max-width: 1200px; margin: 0 auto; }}
header {{ background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin-bottom: 24px; }}
.header-top {{ display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px; }}
h1 {{ font-size: 1.8rem; margin-bottom: 8px; color: #fff; }}
.meta-pills {{ display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px; }}
.pill {{ background: #0f172a; border: 1px solid var(--border); padding: 4px 12px; border-radius: 999px; font-size: 0.85rem; color: var(--text-muted); }}
.scorecards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }}
.card {{ background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 12px; padding: 20px; }}
.card-label {{ font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }}
.card-value {{ font-size: 2rem; font-weight: bold; margin-top: 6px; color: #fff; }}
.card-sub {{ font-size: 0.8rem; color: var(--text-muted); margin-top: 4px; }}
.btn {{ background: var(--accent); color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: 500; font-size: 0.9rem; text-decoration: none; display: inline-block; }}
.btn:hover {{ opacity: 0.9; }}
.btn-print {{ background: #475569; }}
.nav-tabs {{ display: flex; gap: 8px; border-bottom: 1px solid var(--border); margin-bottom: 20px; padding-bottom: 8px; overflow-x: auto; }}
.tab-btn {{ background: transparent; border: none; color: var(--text-muted); padding: 8px 16px; font-size: 1rem; cursor: pointer; border-radius: 6px; font-weight: 500; }}
.tab-btn.active {{ background: var(--accent); color: white; }}
.tab-content {{ display: none; }}
.tab-content.active {{ display: block; }}
.filter-bar {{ display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; align-items: center; }}
.search-input {{ flex: 1; min-width: 250px; background: var(--bg-secondary); border: 1px solid var(--border); padding: 10px 14px; border-radius: 8px; color: white; }}
.filter-btn {{ background: var(--bg-secondary); border: 1px solid var(--border); color: var(--text-muted); padding: 8px 14px; border-radius: 8px; cursor: pointer; }}
.filter-btn.active {{ border-color: var(--accent); color: white; background: #1e3a8a; }}
.finding-card {{ background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 16px; border-left: 6px solid var(--accent); }}
.finding-card.critical {{ border-left-color: var(--critical); }}
.finding-card.high {{ border-left-color: var(--high); }}
.finding-card.medium {{ border-left-color: var(--medium); }}
.finding-card.low {{ border-left-color: var(--low); }}
.badge {{ display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; }}
.badge-critical {{ background: rgba(239, 68, 68, 0.2); color: #fca5a5; }}
.badge-high {{ background: rgba(249, 115, 22, 0.2); color: #fdba74; }}
.badge-medium {{ background: rgba(245, 158, 11, 0.2); color: #fde047; }}
.badge-low {{ background: rgba(16, 185, 129, 0.2); color: #86efac; }}
.badge-pass {{ background: rgba(34, 197, 94, 0.2); color: #86efac; }}
.evidence-box {{ background: #0b1120; border-left: 4px solid #38bdf8; padding: 12px 16px; margin-top: 12px; border-radius: 4px; font-size: 0.9rem; color: #cbd5e1; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 16px; background: var(--bg-secondary); border-radius: 8px; overflow: hidden; }}
th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid var(--border); font-size: 0.9rem; }}
th {{ background: #182234; color: #94a3b8; font-weight: 600; text-transform: uppercase; font-size: 0.8rem; }}
tr:hover {{ background: rgba(255, 255, 255, 0.02); }}
@media print {{
  body {{ background: white; color: black; padding: 0; }}
  header, .card, .finding-card, table {{ background: white; border-color: #ccc; color: black; }}
  .btn, .nav-tabs, .filter-bar {{ display: none; }}
  .tab-content {{ display: block !important; margin-bottom: 30px; }}
}}
</style>
</head>
<body>
<div class="container">
  <header>
    <div class="header-top">
      <div>
        <h1>{html.escape(pack.title)}</h1>
        <p style="color: var(--text-muted);">{html.escape(pack.scope)}</p>
      </div>
      <div>
        <button class="btn btn-print" onclick="window.print()">🖨️ Cetak / Print LHA</button>
      </div>
    </div>
    <div class="meta-pills">
      <span class="pill">Referensi: <b>{html.escape(pack.audit_ref)}</b></span>
      <span class="pill">Lead Auditor: <b>{html.escape(pack.lead_auditor)}</b></span>
      <span class="pill">Domain: <b>{html.escape(pack.domain.value.upper())}</b></span>
      <span class="pill">Tanggal: <b>{pack.created_at[:10]}</b></span>
      <span class="pill">Dokumen: <b>{len(pack.documents)} Berkas</b></span>
    </div>
  </header>

  <div class="scorecards">
    <div class="card">
      <div class="card-label">Skor Kepatuhan (Compliance)</div>
      <div class="card-value" style="color: {('#22c55e' if pack.metrics.compliance_score >= 80 else '#ef4444')};">{pack.metrics.compliance_score:.1f}%</div>
      <div class="card-sub">Standar regulasi & klausul kontrak</div>
    </div>
    <div class="card">
      <div class="card-label">Total Temuan Audit</div>
      <div class="card-value">{pack.metrics.total_findings}</div>
      <div class="card-sub">Kritis: {crit_count} | Tinggi: {high_count} | Sedang: {med_count}</div>
    </div>
    <div class="card">
      <div class="card-label">Akurasi Aritmatika & Pajak</div>
      <div class="card-value">{pack.metrics.arithmetic_accuracy:.1f}%</div>
      <div class="card-sub">Pengujian DPP, PPN 11%, dan totalitas</div>
    </div>
    <div class="card">
      <div class="card-label">Grounding Rate (Bukti Riil)</div>
      <div class="card-value">{pack.metrics.evidence_grounding_rate:.1f}%</div>
      <div class="card-sub">Temuan dengan kutipan dokumen sumber</div>
    </div>
  </div>

  <div class="nav-tabs">
    <button class="tab-btn active" onclick="switchTab('findings')">📋 Temuan Audit ({len(pack.findings)})</button>
    <button class="tab-btn" onclick="switchTab('recon')">⚖️ Rekonsiliasi 3-Way ({len(pack.reconciliations)})</button>
    <button class="tab-btn" onclick="switchTab('kka')">📑 Kertas Kerja (KKA) ({len(pack.working_papers)})</button>
    <button class="tab-btn" onclick="switchTab('action')">🎯 Rencana Aksi ({len(pack.action_plan)})</button>
    <button class="tab-btn" onclick="switchTab('summary')">📖 Ringkasan Eksekutif</button>
  </div>

  <div id="tab-findings" class="tab-content active">
    <div class="filter-bar">
      <input type="text" id="searchInput" class="search-input" placeholder="Cari temuan berdasarkan kata kunci, judul, kondisi..." oninput="filterFindings()">
      <button class="filter-btn active" onclick="setRiskFilter('all', this)">Semua ({len(pack.findings)})</button>
      <button class="filter-btn" onclick="setRiskFilter('critical', this)">Kritis ({crit_count})</button>
      <button class="filter-btn" onclick="setRiskFilter('high', this)">Tinggi ({high_count})</button>
      <button class="filter-btn" onclick="setRiskFilter('medium', this)">Sedang ({med_count})</button>
      <button class="filter-btn" onclick="setRiskFilter('low', this)">Rendah ({low_count})</button>
    </div>
    <div id="findingsContainer"></div>
  </div>

  <div id="tab-recon" class="tab-content">
    <h3>Uji Silang & 3-Way Matching (Kontrak vs BAST vs Invoice vs Pembayaran)</h3>
    <table>
      <thead>
        <tr><th>Uraian Uji Silang</th><th>Rincian Dokumen</th><th>Selisih</th><th>Status</th></tr>
      </thead>
      <tbody>{recon_rows or "<tr><td colspan='4'>Tidak ada rekonsiliasi yang tercatat.</td></tr>"}</tbody>
    </table>
  </div>

  <div id="tab-kka" class="tab-content">
    <h3>Kertas Kerja Audit (Audit Working Papers)</h3>
    <table>
      <thead>
        <tr><th>Ref KKA</th><th>Prosedur</th><th>Dokumen</th><th>Hasil</th><th>Catatan</th><th>Ref Temuan</th></tr>
      </thead>
      <tbody>{kka_rows or "<tr><td colspan='6'>Tidak ada kertas kerja tercatat.</td></tr>"}</tbody>
    </table>
  </div>

  <div id="tab-action" class="tab-content">
    <h3>Matriks Rencana Aksi & Tindak Lanjut</h3>
    <table>
      <thead>
        <tr><th>No</th><th>ID Temuan</th><th>Prioritas</th><th>Langkah Perbaikan</th><th>Batas Waktu</th><th>PIC</th></tr>
      </thead>
      <tbody>{action_rows or "<tr><td colspan='6'>Tidak ada rencana aksi tercatat.</td></tr>"}</tbody>
    </table>
  </div>

  <div id="tab-summary" class="tab-content">
    <div class="card" style="white-space: pre-wrap; font-family: inherit;">{html.escape(pack.executive_summary)}</div>
  </div>

</div>

<script>
const findingsData = {findings_json};
let activeRisk = 'all';

function renderFindings(items) {{
  const container = document.getElementById('findingsContainer');
  if (items.length === 0) {{
    container.innerHTML = '<div class="card" style="text-align: center; color: var(--text-muted);">Tidak ada temuan yang cocok dengan filter pencarian.</div>';
    return;
  }}
  container.innerHTML = items.map(f => `
    <div class="finding-card ${{f.risk}}">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <div>
          <span class="badge badge-${{f.risk}}">${{f.risk.toUpperCase()}}</span>
          <span style="font-size: 0.85rem; color: var(--text-muted); margin-left: 8px;"><code>${{f.id}}</code> · ${{f.category}}</span>
        </div>
      </div>
      <h3 style="margin-bottom: 12px; color: #fff;">${{f.title}}</h3>
      <div style="display: grid; grid-template-columns: 1fr; gap: 8px; font-size: 0.92rem;">
        <div><b>🔍 Kondisi (Condition):</b> ${{f.condition}}</div>
        <div><b>📏 Kriteria (Criteria):</b> ${{f.criteria}}</div>
        <div><b>⚡ Sebab (Cause):</b> ${{f.cause}}</div>
        <div><b>⚠️ Akibat & Risiko (Consequence):</b> ${{f.consequence}}</div>
        <div style="margin-top: 6px; padding: 10px; background: rgba(59, 130, 246, 0.1); border-left: 3px solid var(--accent); border-radius: 4px;">
          <b>💡 Rekomendasi:</b> ${{f.recommendation}}
        </div>
      </div>
      ${{f.evidence && f.evidence.length > 0 ? `
        <div class="evidence-box">
          <b>📄 Bukti Dokumen Terverifikasi:</b><br>
          ${{f.evidence.map(e => `<div>• <b>${{e.document}}</b> (${{e.locator}}): <i>"${{e.excerpt}}"</i></div>`).join('')}}
        </div>
      ` : ''}}
    </div>
  `).join('');
}}

function filterFindings() {{
  const query = document.getElementById('searchInput').value.toLowerCase();
  const filtered = findingsData.filter(f => {{
    const matchRisk = (activeRisk === 'all' || f.risk === activeRisk);
    const textCorpus = (f.title + ' ' + f.condition + ' ' + f.criteria + ' ' + f.cause + ' ' + f.consequence + ' ' + f.recommendation + ' ' + f.id).toLowerCase();
    const matchQuery = !query || textCorpus.includes(query);
    return matchRisk && matchQuery;
  }});
  renderFindings(filtered);
}}

function setRiskFilter(risk, btn) {{
  activeRisk = risk;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  filterFindings();
}}

function switchTab(tabId) {{
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
  document.getElementById('tab-' + tabId).classList.add('active');
  event.target.classList.add('active');
}}

// Initialize findings list
renderFindings(findingsData);
</script>
</body>
</html>
"""

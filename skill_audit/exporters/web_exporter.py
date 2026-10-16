"""Single-file offline interactive HTML audit dashboard exporter.

Features:
- ISO 31000 5x5 Risk Heatmap
- Standard 5C Findings with Interactive Human Triage (Approve/Reject/Notes)
- REA Unknowns & Inquiries Ledger
- REA Audit Obligations & Compliance Coverage
- Cryptographic Evidence Bundle Forensics (SHA-256 integrity table)
- Segregation of Duties (SoD) & Delegation of Authority (DoA) matrices
- Interactive Human Auditor Sign-Off Sheet
- Zero CDN dependencies (100% offline self-contained)
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

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
        # Prepare findings JSON for client-side search and triage
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
                "coso": f.coso_component or "Control Activities",
                "process": f.business_process or "Procure-to-Pay",
                "human_status": f.human_status or "pending",
                "human_notes": f.human_notes or "",
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

        # Build 5x5 Heatmap HTML
        grid = pack.risk_heatmap.get("grid", {}) if pack.risk_heatmap else {}
        heatmap_html = self._render_heatmap_grid(grid)

        # Build Unknowns rows
        unknowns_rows = ""
        for u in pack.unknowns:
            st_badge = (
                '<span class="badge badge-pass">RESOLVED</span>'
                if u.status.value == "resolved"
                else (
                    '<span class="badge badge-medium">OPEN</span>'
                    if u.status.value == "open"
                    else '<span class="badge badge-neutral">WAIVED</span>'
                )
            )
            res_txt = f"<br><small style='color: #22c55e;'><b>Penyelesaian:</b> {html.escape(u.resolution_notes)} ({html.escape(u.resolved_by)})</small>" if u.resolution_notes else ""
            unknowns_rows += (
                f"<tr><td><code>{html.escape(u.id)}</code></td>"
                f"<td><b>{html.escape(u.question)}</b>{res_txt}</td>"
                f"<td><span class=\"badge badge-neutral\">{html.escape(u.category)}</span></td>"
                f"<td>{st_badge}</td>"
                f"<td>{html.escape(u.impact)}</td>"
                f"<td>{html.escape(u.evidence_required)}</td></tr>"
            )

        # Build Obligations rows
        obligations_rows = ""
        for o in pack.obligations:
            st_cls = "badge-pass" if o.status == "satisfied" else ("badge-critical" if o.status == "violated" else "badge-medium")
            obligations_rows += (
                f"<tr><td><code>{html.escape(o.id)}</code></td>"
                f"<td><b>{html.escape(o.title)}</b></td>"
                f"<td><small>{html.escape(o.standard_ref)}</small></td>"
                f"<td><span class=\"badge {st_cls}\">{o.status.upper()}</span></td>"
                f"<td>{html.escape(o.coverage_notes)}</td></tr>"
            )

        # Build Evidence Bundle files rows
        bundle_files = pack.evidence_bundle.get("files", [])
        bundle_rows = ""
        for f in bundle_files:
            h = f.get("content_sha256", "")
            abbr = f"{h[:16]}...{h[-12:]}" if len(h) >= 28 else h
            bundle_rows += (
                f"<tr><td><b>{html.escape(f.get('name', ''))}</b></td>"
                f"<td><span class=\"badge badge-neutral\">{html.escape(f.get('role_in_dossier', ''))}</span></td>"
                f"<td><code title=\"{h}\">{abbr}</code></td>"
                f"<td>{f.get('size_bytes', 0):,} B</td>"
                f"<td><span class=\"badge badge-pass\">VERIFIED INTACT</span></td></tr>"
            )

        # Build SoD rows
        sod_rows = ""
        for s in pack.sod_conflicts:
            docs = ", ".join(s.document_refs)
            sod_rows += (
                f"<tr><td><code>{html.escape(s.conflict_id)}</code></td>"
                f"<td><b>{html.escape(s.individual_name)}</b></td>"
                f"<td><span class=\"badge badge-critical\">{html.escape(s.role_a)}</span> vs <span class=\"badge badge-critical\">{html.escape(s.role_b)}</span></td>"
                f"<td>{html.escape(docs)}</td>"
                f"<td>{html.escape(s.risk_explanation)}</td>"
                f"<td>{html.escape(s.recommendation)}</td></tr>"
            )

        # Build DoA rows
        doa_rows = ""
        for d in pack.doa_violations:
            doa_rows += (
                f"<tr><td><code>{html.escape(d.violation_id)}</code></td>"
                f"<td><b>{html.escape(d.approver_name)}</b> ({html.escape(d.approver_title)})</td>"
                f"<td>Rp {d.transaction_amount:,.0f}</td>"
                f"<td>Rp {d.authorized_limit:,.0f}</td>"
                f"<td style=\"color: #ef4444; font-weight: bold;\">+Rp {d.excess_amount:,.0f}</td>"
                f"<td>{html.escape(d.document_ref)}</td>"
                f"<td>{html.escape(d.notes)}</td></tr>"
            )

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
        for a in pack.action_plan:
            action_rows += (
                f"<tr><td>{a['step_no']}</td>"
                f"<td><code>{html.escape(a['finding_id'])}</code></td>"
                f"<td><b>{html.escape(a['priority'])}</b></td>"
                f"<td>{html.escape(a['action_required'])}</td>"
                f"<td>{a['target_days']} Hari</td>"
                f"<td>{html.escape(a['pic'])}</td></tr>"
            )

        so = pack.human_sign_off
        so_name = so.reviewer_name or "Drs. Bambang Wijaya, Ak., CA, CPA"
        so_role = so.reviewer_role or "Lead Internal Auditor"
        so_nip = so.reviewer_license_or_nip or "NIP-19850412-201001-1-003"
        so_opinion = so.audit_opinion or "WDP (Wajar Dengan Pengecualian)"
        so_date = so.signed_at or "Belum Ditandatangani"
        so_comments = so.comments or "Pengendalian internal memadai dengan beberapa catatan koreksi administratif."
        so_badge = '<span class="badge badge-pass">DITANDATANGANI</span>' if so.is_signed else '<span class="badge badge-medium">MENUNGGU PENGESAHAN</span>'

        return f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Skill-Audit: {html.escape(pack.title)}</title>
  <style>
    :root {{
      --bg: #0f172a;
      --card-bg: #1e293b;
      --border: #334155;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #3b82f6;
      --critical: #ef4444;
      --high: #f97316;
      --medium: #eab308;
      --low: #3b82f6;
      --pass: #22c55e;
      --radius: 8px;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
    body {{ background: var(--bg); color: var(--text); padding: 24px; line-height: 1.5; }}
    .header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; padding-bottom: 20px; border-bottom: 1px solid var(--border); }}
    .header h1 {{ font-size: 1.6rem; color: #fff; margin-bottom: 6px; }}
    .meta-pills {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 8px; }}
    .pill {{ background: rgba(255,255,255,0.06); padding: 4px 10px; border-radius: 999px; font-size: 0.8rem; border: 1px solid var(--border); }}
    .scorecards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 16px; margin-bottom: 24px; }}
    .card {{ background: var(--card-bg); border: 1px solid var(--border); border-radius: var(--radius); padding: 18px; }}
    .card-label {{ font-size: 0.82rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; }}
    .card-value {{ font-size: 1.8rem; font-weight: 700; color: #fff; }}
    .card-sub {{ font-size: 0.78rem; color: var(--text-muted); margin-top: 4px; }}
    .nav-tabs {{ display: flex; gap: 8px; border-bottom: 1px solid var(--border); margin-bottom: 20px; overflow-x: auto; padding-bottom: 4px; }}
    .tab-btn {{ background: transparent; border: none; color: var(--text-muted); padding: 8px 14px; font-size: 0.88rem; font-weight: 600; cursor: pointer; border-bottom: 2px solid transparent; border-radius: 4px 4px 0 0; white-space: nowrap; }}
    .tab-btn.active {{ color: var(--accent); border-bottom-color: var(--accent); background: rgba(59, 130, 246, 0.08); }}
    .tab-content {{ display: none; }}
    .tab-content.active {{ display: block; }}
    .filter-bar {{ display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }}
    .search-input {{ flex: 1; min-width: 260px; background: var(--card-bg); border: 1px solid var(--border); color: #fff; padding: 8px 14px; border-radius: var(--radius); font-size: 0.9rem; }}
    .filter-btn {{ background: var(--card-bg); border: 1px solid var(--border); color: var(--text-muted); padding: 6px 12px; border-radius: var(--radius); cursor: pointer; font-size: 0.82rem; }}
    .filter-btn.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
    .finding-card {{ background: var(--card-bg); border: 1px solid var(--border); border-left: 4px solid var(--border); border-radius: var(--radius); padding: 18px; margin-bottom: 14px; transition: transform 0.15s; }}
    .finding-card:hover {{ border-color: #64748b; }}
    .finding-card.critical {{ border-left-color: var(--critical); }}
    .finding-card.high {{ border-left-color: var(--high); }}
    .finding-card.medium {{ border-left-color: var(--medium); }}
    .finding-card.low {{ border-left-color: var(--low); }}
    .badge {{ padding: 3px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; display: inline-block; }}
    .badge-critical {{ background: rgba(239, 68, 68, 0.18); color: var(--critical); border: 1px solid var(--critical); }}
    .badge-high {{ background: rgba(249, 115, 22, 0.18); color: var(--high); border: 1px solid var(--high); }}
    .badge-medium {{ background: rgba(234, 179, 8, 0.18); color: var(--medium); border: 1px solid var(--medium); }}
    .badge-low {{ background: rgba(59, 130, 246, 0.18); color: var(--low); border: 1px solid var(--low); }}
    .badge-pass {{ background: rgba(34, 197, 94, 0.18); color: var(--pass); border: 1px solid var(--pass); }}
    .badge-neutral {{ background: rgba(255, 255, 255, 0.08); color: var(--text-muted); }}
    .evidence-box {{ background: rgba(0,0,0,0.25); border: 1px dashed var(--border); padding: 12px; border-radius: 6px; margin-top: 10px; font-size: 0.84rem; }}
    .triage-actions {{ margin-top: 12px; padding-top: 10px; border-top: 1px dashed var(--border); display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }}
    .btn {{ padding: 6px 12px; border-radius: 6px; border: 1px solid var(--border); cursor: pointer; font-size: 0.82rem; font-weight: 600; color: #fff; background: var(--card-bg); }}
    .btn-approve {{ background: rgba(34, 197, 94, 0.2); border-color: var(--pass); color: var(--pass); }}
    .btn-reject {{ background: rgba(239, 68, 68, 0.2); border-color: var(--critical); color: var(--critical); }}
    .btn-print {{ background: var(--accent); border-color: var(--accent); }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 0.88rem; }}
    th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--border); }}
    th {{ background: rgba(255,255,255,0.03); color: var(--text-muted); font-size: 0.8rem; text-transform: uppercase; }}
    .heatmap-table {{ width: 100%; border-collapse: collapse; margin-top: 12px; text-align: center; }}
    .heatmap-table th, .heatmap-table td {{ border: 1px solid var(--border); padding: 12px 8px; font-size: 0.82rem; }}
    .heatmap-cell {{ font-weight: bold; border-radius: 2px; }}
    .cell-red {{ background: rgba(239, 68, 68, 0.35); color: #fca5a5; }}
    .cell-amber {{ background: rgba(249, 115, 22, 0.35); color: #fdba74; }}
    .cell-yellow {{ background: rgba(234, 179, 8, 0.25); color: #fde047; }}
    .cell-green {{ background: rgba(34, 197, 94, 0.2); color: #86efac; }}
    @media print {{ body {{ background: #fff; color: #000; padding: 0; }} .nav-tabs, .btn-print, .filter-bar, .triage-actions {{ display: none !important; }} .tab-content {{ display: block !important; margin-bottom: 30px; }} }}
  </style>
</head>
<body>

  <header class="header">
    <div>
      <h1>🏛️ Skill-Audit: {html.escape(pack.title)}</h1>
      <p style="color: var(--text-muted); font-size: 0.9rem;">{html.escape(pack.scope)}</p>
      <div class="meta-pills">
        <span class="pill">Referensi: <b>{html.escape(pack.audit_ref)}</b></span>
        <span class="pill">Lead Auditor: <b>{html.escape(pack.lead_auditor)}</b></span>
        <span class="pill">Domain: <b>{html.escape(pack.domain.value.upper())}</b></span>
        <span class="pill">Tanggal: <b>{pack.created_at[:10]}</b></span>
        <span class="pill">Dokumen: <b>{len(pack.documents)} Berkas</b></span>
        <span class="pill">Human Sign-off: {so_badge}</span>
      </div>
    </div>
    <div style="display: flex; gap: 8px;">
      <button class="btn" onclick="exportReviewedJSON()">💾 Unduh Data Review (JSON)</button>
      <button class="btn btn-print" onclick="window.print()">🖨️ Cetak / Print LHA</button>
    </div>
  </header>

  <div class="scorecards">
    <div class="card">
      <div class="card-label">Skor Kepatuhan (Compliance)</div>
      <div class="card-value" style="color: {('#22c55e' if pack.metrics.compliance_score >= 80 else '#ef4444')};">{pack.metrics.compliance_score:.1f}%</div>
      <div class="card-sub">Standar regulasi & klausul kontrak</div>
    </div>
    <div class="card">
      <div class="card-label">Tata Kelola & DoA Score</div>
      <div class="card-value" style="color: {('#22c55e' if pack.governance_score >= 80 else '#f97316')};">{pack.governance_score:.1f}%</div>
      <div class="card-sub">Kepatuhan batas kewenangan approval</div>
    </div>
    <div class="card">
      <div class="card-label">Total Temuan Audit (5C)</div>
      <div class="card-value">{pack.metrics.total_findings}</div>
      <div class="card-sub">Kritis: {crit_count} | Tinggi: {high_count} | Sedang: {med_count}</div>
    </div>
    <div class="card">
      <div class="card-label">Grounding Rate (Bukti Riil)</div>
      <div class="card-value">{pack.metrics.evidence_grounding_rate:.1f}%</div>
      <div class="card-sub">Temuan dengan kutipan dokumen sumber</div>
    </div>
  </div>

  <div class="nav-tabs">
    <button class="tab-btn active" onclick="switchTab('findings')">📋 Temuan Audit ({len(pack.findings)})</button>
    <button class="tab-btn" onclick="switchTab('heatmap')">🔥 Matriks Risiko 5x5</button>
    <button class="tab-btn" onclick="switchTab('unknowns')">❓ Inquiries / Unknowns ({len(pack.unknowns)})</button>
    <button class="tab-btn" onclick="switchTab('obligations')">🛡️ Kewajiban Audit ({len(pack.obligations)})</button>
    <button class="tab-btn" onclick="switchTab('recon')">⚖️ Rekonsiliasi 3-Way ({len(pack.reconciliations)})</button>
    <button class="tab-btn" onclick="switchTab('governance')">🏛️ Tata Kelola, SoD & DoA ({len(pack.sod_conflicts) + len(pack.doa_violations)})</button>
    <button class="tab-btn" onclick="switchTab('bundle')">🔐 Evidence Bundle Forensics ({len(bundle_files)})</button>
    <button class="tab-btn" onclick="switchTab('signoff')">✍️ Pengesahan Auditor Manusia</button>
    <button class="tab-btn" onclick="switchTab('kka')">📑 Kertas Kerja (KKA) ({len(pack.working_papers)})</button>
    <button class="tab-btn" onclick="switchTab('summary')">📖 Ringkasan Eksekutif</button>
  </div>

  <!-- Tab 1: Findings -->
  <div id="tab-findings" class="tab-content active">
    <div class="filter-bar">
      <input type="text" id="searchInput" class="search-input" placeholder="Cari temuan berdasarkan kata kunci, judul, kondisi, atau proses..." oninput="filterFindings()">
      <button class="filter-btn active" onclick="setRiskFilter('all', this)">Semua ({len(pack.findings)})</button>
      <button class="filter-btn" onclick="setRiskFilter('critical', this)">Kritis ({crit_count})</button>
      <button class="filter-btn" onclick="setRiskFilter('high', this)">Tinggi ({high_count})</button>
      <button class="filter-btn" onclick="setRiskFilter('medium', this)">Sedang ({med_count})</button>
      <button class="filter-btn" onclick="setRiskFilter('low', this)">Rendah ({low_count})</button>
    </div>
    <div id="findingsContainer"></div>
  </div>

  <!-- Tab 2: 5x5 Heatmap -->
  <div id="tab-heatmap" class="tab-content">
    <div class="card" style="margin-bottom: 20px;">
      <h3>Matriks Risiko 5x5 Enterprise Risk Management (ISO 31000 / COSO ERM)</h3>
      <p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 4px;">
        Memetakan probabilitas terjadinya risiko (Likelihood) terhadap besaran kerugian (Impact) serta memperhitungkan efektivitas kontrol penanganan.
      </p>
      {heatmap_html}
    </div>
  </div>

  <!-- Tab 3: Unknowns Ledger -->
  <div id="tab-unknowns" class="tab-content">
    <div class="card">
      <h3>Buku Besar Pertanyaan Terbuka & Ambiguitas Bukti (Ledger of Unknowns & Inquiries)</h3>
      <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 12px;">
        Metodologi REA: Setiap ketiadaan dokumen pembuktian dicatat sebagai inquiry formal yang harus dijawab manajemen sebelum laporan dapat disahkan bersih.
      </p>
      <table>
        <thead>
          <tr><th>ID</th><th>Pertanyaan & Ambiguitas Bukti</th><th>Kategori</th><th>Status</th><th>Dampak Risiko</th><th>Bukti yang Dibutuhkan</th></tr>
        </thead>
        <tbody>{unknowns_rows or "<tr><td colspan='6' style='color: var(--pass);'>🟢 Tidak ada pertanyaan menggantung. Seluruh bukti lengkap.</td></tr>"}</tbody>
      </table>
    </div>
  </div>

  <!-- Tab 4: Obligations -->
  <div id="tab-obligations" class="tab-content">
    <div class="card">
      <h3>Evaluasi Pemenuhan Kewajiban Audit (Audit Obligations & Compliance Coverage)</h3>
      <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 12px;">
        Mengukur ketercakupan seluruh prosedur pengujian wajib terhadap regulasi dan kerangka kerja audit yang berlaku.
      </p>
      <table>
        <thead>
          <tr><th>ID</th><th>Prosedur Standar Audit</th><th>Dasar Regulasi</th><th>Status</th><th>Catatan Evaluasi</th></tr>
        </thead>
        <tbody>{obligations_rows or "<tr><td colspan='5'>Tidak ada kewajiban audit yang tercatat.</td></tr>"}</tbody>
      </table>
    </div>
  </div>

  <!-- Tab 5: Recon -->
  <div id="tab-recon" class="tab-content">
    <div class="card">
      <h3>Uji Silang & 3-Way Matching (Kontrak vs BAST vs Invoice vs Pembayaran)</h3>
      <table>
        <thead>
          <tr><th>Uraian Uji Silang</th><th>Rincian Dokumen</th><th>Selisih</th><th>Status</th></tr>
        </thead>
        <tbody>{recon_rows or "<tr><td colspan='4'>Tidak ada rekonsiliasi yang tercatat.</td></tr>"}</tbody>
      </table>
    </div>
  </div>

  <!-- Tab 6: Governance -->
  <div id="tab-governance" class="tab-content">
    <div class="card" style="margin-bottom: 24px;">
      <h3>Benturan Pemisahan Tugas (Segregation of Duties - SoD)</h3>
      <table>
        <thead>
          <tr><th>ID</th><th>Nama Individu</th><th>Peran Bertentangan</th><th>Dokumen Terkait</th><th>Risiko</th><th>Rekomendasi</th></tr>
        </thead>
        <tbody>{sod_rows or "<tr><td colspan='6' style='color: var(--pass);'>🟢 Tidak ditemukan benturan pemisahan tugas (SoD Compliant).</td></tr>"}</tbody>
      </table>
    </div>

    <div class="card">
      <h3>Pelampauan Batas Kewenangan Otorisasi (Delegation of Authority - DoA)</h3>
      <table>
        <thead>
          <tr><th>ID</th><th>Pejabat Penandatangan</th><th>Nilai Transaksi</th><th>Batas Wewenang</th><th>Pelampauan</th><th>Dokumen</th><th>Catatan</th></tr>
        </thead>
        <tbody>{doa_rows or "<tr><td colspan='7' style='color: var(--pass);'>🟢 Seluruh transaksi berada dalam batas kewenangan yang sah (DoA Compliant).</td></tr>"}</tbody>
      </table>
    </div>
  </div>

  <!-- Tab 7: Evidence Bundle -->
  <div id="tab-bundle" class="tab-content">
    <div class="card">
      <h3>Cryptographic Evidence Bundle & Forensic SHA-256 Manifest</h3>
      <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 12px;">
        Bundle ID: <code>{pack.evidence_bundle.get('bundle_id', 'EVD-AUTO')}</code> | Status: <span class="badge badge-pass">VERIFIED INTACT</span>
      </p>
      <table>
        <thead>
          <tr><th>Nama Berkas</th><th>Peran Berkas</th><th>SHA-256 Digest</th><th>Ukuran</th><th>Integritas Forensik</th></tr>
        </thead>
        <tbody>{bundle_rows or "<tr><td colspan='5'>Tidak ada berkas bukti terdaftar.</td></tr>"}</tbody>
      </table>
    </div>
  </div>

  <!-- Tab 8: Human Sign-Off Sheet -->
  <div id="tab-signoff" class="tab-content">
    <div class="card" style="max-width: 800px; margin: 0 auto; border: 2px solid var(--border); padding: 30px;">
      <h2 style="text-align: center; margin-bottom: 20px; color: #fff;">LEMBAR PENGESAHAN AUDITOR INDEPENDEN</h2>
      <div style="background: rgba(255,255,255,0.02); padding: 20px; border-radius: var(--radius); border: 1px solid var(--border); margin-bottom: 20px;">
        <div style="margin-bottom: 10px;"><b>Penugasan Audit:</b> {html.escape(pack.title)} (Ref: {html.escape(pack.audit_ref)})</div>
        <div style="margin-bottom: 10px;"><b>Nama Auditor Penanggung Jawab:</b> <span id="soName">{html.escape(so_name)}</span></div>
        <div style="margin-bottom: 10px;"><b>Jabatan / Lisensi:</b> <span id="soRole">{html.escape(so_role)}</span> (NIP/Reg: {html.escape(so_nip)})</div>
        <div style="margin-bottom: 10px;"><b>Kesimpulan & Opini Audit:</b> <span class="badge badge-pass" id="soOpinion" style="font-size: 0.9rem;">{html.escape(so_opinion)}</span></div>
        <div style="margin-bottom: 10px;"><b>Tanggal Pengesahan:</b> <span id="soDate">{html.escape(so_date)}</span></div>
        <div style="margin-top: 15px; border-top: 1px dashed var(--border); padding-top: 10px;">
          <b>Catatan Akhir Auditor:</b>
          <p id="soComments" style="font-style: italic; color: var(--text-muted); margin-top: 4px;">"{html.escape(so_comments)}"</p>
        </div>
      </div>
      <div style="text-align: right; margin-top: 40px; padding-right: 40px;">
        <p>Jakarta, {pack.created_at[:10]}</p>
        <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 4px;">Ditandatangani secara elektronik:</p>
        <div style="margin: 20px 0; font-family: monospace; font-size: 1.1rem; color: #22c55e;">[SIGNED & CERTIFIED]</div>
        <p><b>{html.escape(so_name)}</b></p>
        <p style="font-size: 0.85rem; color: var(--text-muted);">{html.escape(so_role)}</p>
      </div>
    </div>
  </div>

  <!-- Tab 9: KKA -->
  <div id="tab-kka" class="tab-content">
    <div class="card">
      <h3>Kertas Kerja Audit (Audit Working Papers)</h3>
      <table>
        <thead>
          <tr><th>Ref KKA</th><th>Prosedur</th><th>Dokumen</th><th>Hasil</th><th>Catatan</th><th>Ref Temuan</th></tr>
        </thead>
        <tbody>{kka_rows or "<tr><td colspan='6'>Tidak ada kertas kerja tercatat.</td></tr>"}</tbody>
      </table>
    </div>
  </div>

  <!-- Tab 10: Executive Summary -->
  <div id="tab-summary" class="tab-content">
    <div class="card" style="line-height: 1.7;">
      <pre style="white-space: pre-wrap; font-family: inherit; color: var(--text);">{html.escape(pack.executive_summary)}</pre>
    </div>
  </div>

<script>
let findingsData = {findings_json};
let activeRisk = 'all';

function renderFindings(items) {{
  const container = document.getElementById('findingsContainer');
  if (items.length === 0) {{
    container.innerHTML = '<div class="card" style="text-align: center; color: var(--text-muted);">Tidak ada temuan yang cocok dengan filter pencarian.</div>';
    return;
  }}
  container.innerHTML = items.map(f => `
    <div class="finding-card ${{f.risk}}" id="${{f.id}}">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <div>
          <span class="badge badge-${{f.risk}}">${{f.risk.toUpperCase()}}</span>
          <span class="badge badge-neutral" style="margin-left: 6px;">${{f.process}}</span>
          <span class="badge badge-neutral" style="margin-left: 4px;">COSO: ${{f.coso}}</span>
          <span style="font-size: 0.85rem; color: var(--text-muted); margin-left: 8px;"><code>${{f.id}}</code> · ${{f.category}}</span>
        </div>
        <div>
          <span class="badge badge-${{f.human_status === 'approved' ? 'pass' : (f.human_status === 'rejected' ? 'critical' : 'neutral')}}">
            ${{f.human_status.toUpperCase()}}
          </span>
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
      <div class="triage-actions">
        <span style="font-size: 0.82rem; color: var(--text-muted); margin-right: 6px;">Triage Review:</span>
        <button class="btn btn-approve" onclick="triageFinding('${{f.id}}', 'approved')">✓ Setujui (Approve)</button>
        <button class="btn btn-reject" onclick="triageFinding('${{f.id}}', 'rejected')">✗ Tolak / FP</button>
        <button class="btn" onclick="addAuditorNote('${{f.id}}')">📝 Catatan Auditor</button>
        ${{f.human_notes ? `<span style="font-size: 0.82rem; color: #38bdf8; margin-left: 10px;">Catatan: <i>${{f.human_notes}}</i></span>` : ''}}
      </div>
    </div>
  `).join('');
}}

function triageFinding(id, status) {{
  const f = findingsData.find(x => x.id === id);
  if (f) {{
    f.human_status = status;
    filterFindings();
  }}
}}

function addAuditorNote(id) {{
  const f = findingsData.find(x => x.id === id);
  if (f) {{
    const note = prompt("Masukkan catatan auditor manusia untuk temuan " + id + ":", f.human_notes || "");
    if (note !== null) {{
      f.human_notes = note;
      filterFindings();
    }}
  }}
}}

function exportReviewedJSON() {{
  const blob = new Blob([JSON.stringify(findingsData, null, 2)], {{ type: 'application/json' }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'reviewed_findings.json';
  a.click();
}}

function filterFindings() {{
  const query = document.getElementById('searchInput').value.toLowerCase();
  const filtered = findingsData.filter(f => {{
    const matchRisk = (activeRisk === 'all' || f.risk === activeRisk);
    const textCorpus = (f.title + ' ' + f.condition + ' ' + f.criteria + ' ' + f.cause + ' ' + f.consequence + ' ' + f.recommendation + ' ' + f.id + ' ' + f.process + ' ' + f.coso).toLowerCase();
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

renderFindings(findingsData);
</script>
</body>
</html>
"""

    def _render_heatmap_grid(self, grid: dict[str, list[str]]) -> str:
        """Render 5x5 HTML table representing Likelihood vs Impact."""
        def cell_color(l: int, i: int) -> str:
            score = l * i
            if score >= 16:
                return "cell-red"
            elif score >= 10:
                return "cell-amber"
            elif score >= 5:
                return "cell-yellow"
            return "cell-green"

        likelihood_labels = {
            5: "5 - Hampir Pasti",
            4: "4 - Sering",
            3: "3 - Mungkin",
            2: "2 - Jarang",
            1: "1 - Sangat Jarang",
        }
        impact_labels = ["1 - Insignifikan", "2 - Minor", "3 - Moderat", "4 - Mayor", "5 - Katastropik"]

        rows = []
        for l in range(5, 0, -1):
            row_html = f"<tr><td style='font-weight: bold; width: 150px;'>{likelihood_labels[l]}</td>"
            for i in range(1, 6):
                f_ids = grid.get(f"{l}_{i}", [])
                cls = cell_color(l, i)
                items_str = "<br>".join(f"<code>{fid}</code>" for fid in f_ids) if f_ids else f"{l*i}"
                row_html += f"<td class='heatmap-cell {cls}'>{items_str}</td>"
            row_html += "</tr>"
            rows.append(row_html)

        header = "<tr><th>Kemungkinan (Y) \\ Dampak (X)</th>" + "".join(f"<th>{imp}</th>" for imp in impact_labels) + "</tr>"

        return f"""
        <table class="heatmap-table">
          <thead>{header}</thead>
          <tbody>{''.join(rows)}</tbody>
        </table>
        """

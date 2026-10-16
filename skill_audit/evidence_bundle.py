"""Cryptographic Evidence Bundle and Provenance Manager (inspired by REA architecture).

Provides:
- SHA-256 evidence integrity hashing for each source document
- Strict provenance tracking with untrusted content isolation (_meta.provenance.untrusted_content)
- Forensic verification against document tampering
- Exportable/importable evidence packages (.zip / .json)
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from skill_audit.models import AuditDocument, AuditPack, EvidenceBundleManifest


def compute_bytes_sha256(data: bytes) -> str:
    """Compute SHA-256 hash for raw byte content."""
    return hashlib.sha256(data).hexdigest()


def compute_string_sha256(text: str) -> str:
    """Compute SHA-256 hash for utf-8 text."""
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def create_evidence_bundle(
    documents: list[AuditDocument],
    bundle_id: str | None = None,
) -> EvidenceBundleManifest:
    """Build a cryptographic evidence bundle with SHA-256 digests and provenance markers."""
    bid = bundle_id or f"EVD-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    files_manifest: list[dict[str, Any]] = []

    for doc in documents:
        content_hash = compute_string_sha256(doc.content)

        # Check physical file if it exists on disk
        disk_hash = None
        file_size = len(doc.content.encode("utf-8"))
        if doc.path and Path(doc.path).exists():
            try:
                raw_bytes = Path(doc.path).read_bytes()
                disk_hash = compute_bytes_sha256(raw_bytes)
                file_size = len(raw_bytes)
            except Exception:
                disk_hash = content_hash

        files_manifest.append({
            "name": doc.name,
            "path": str(doc.path),
            "doc_type": doc.doc_type.value,
            "role_in_dossier": doc.role_in_dossier,
            "content_sha256": content_hash,
            "file_sha256": disk_hash or content_hash,
            "size_bytes": file_size,
            "chunks_count": len(doc.chunks),
            "entities_detected": {k: len(v) if isinstance(v, list) else v for k, v in doc.entities.items()},
            # REA Security Boundary: mark analyzed text as untrusted content to protect AI agents
            "_meta": {
                "provenance": {
                    "untrusted_content": True,
                    "extracted_at": datetime.now(timezone.utc).isoformat(),
                    "source": "AuditEvidenceEngine",
                }
            },
        })

    return EvidenceBundleManifest(
        bundle_id=bid,
        created_at=datetime.now(timezone.utc).isoformat(),
        files=files_manifest,
        total_files=len(files_manifest),
        integrity_status="verified_intact",
    )


def verify_evidence_bundle(
    bundle_manifest: dict[str, Any] | EvidenceBundleManifest,
    documents: list[AuditDocument],
) -> dict[str, Any]:
    """Forensically verify documents against bundle manifest digests to detect tampering."""
    manifest_dict = bundle_manifest.to_dict() if hasattr(bundle_manifest, "to_dict") else dict(bundle_manifest)
    manifest_files = {f["name"]: f for f in manifest_dict.get("files", [])}

    results: list[dict[str, Any]] = []
    tampered_count = 0

    for doc in documents:
        expected = manifest_files.get(doc.name)
        if not expected:
            results.append({
                "document": doc.name,
                "status": "UNTRACKED",
                "notes": "Document was not recorded in initial evidence manifest.",
            })
            continue

        raw_text = doc.content
        if not raw_text and doc.path and Path(doc.path).exists():
            try:
                raw_text = Path(doc.path).read_text(encoding="utf-8", errors="replace")
            except Exception:
                pass

        current_hash = compute_string_sha256(raw_text) if raw_text else None
        expected_hash = expected.get("content_sha256")

        # Also check physical disk bytes
        disk_hash = None
        if doc.path and Path(doc.path).exists():
            try:
                disk_hash = compute_bytes_sha256(Path(doc.path).read_bytes())
            except Exception:
                pass
        expected_file_hash = expected.get("file_sha256")

        is_intact = (current_hash and current_hash == expected_hash) or (disk_hash and disk_hash == expected_file_hash)

        if is_intact:
            results.append({
                "document": doc.name,
                "status": "VERIFIED_INTACT",
                "sha256": current_hash or disk_hash,
            })
        else:
            tampered_count += 1
            results.append({
                "document": doc.name,
                "status": "TAMPERED_COMPROMISED",
                "expected_sha256": expected_hash or expected_file_hash,
                "actual_sha256": current_hash or disk_hash,
                "notes": "Hash mismatch detected! Document content was altered after bundle creation.",
            })

    return {
        "verified_intact": tampered_count == 0,
        "total_checked": len(documents),
        "tampered_count": tampered_count,
        "details": results,
    }


def export_evidence_bundle_zip(pack: AuditPack, output_zip_path: str | Path) -> Path:
    """Export standalone, court-defensible cryptographic Evidence Bundle ZIP archive."""
    out_path = Path(output_zip_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. Manifest
        manifest_data = pack.evidence_bundle or create_evidence_bundle(pack.documents, f"EVD-{pack.audit_ref}").to_dict()
        zf.writestr("manifest.json", json.dumps(manifest_data, indent=2))

        # 2. Audit Pack YAML
        zf.writestr(f"{pack.audit_ref}_pack.yaml", pack.to_yaml())

        # 3. Source Documents & Provenance metadata
        for doc in pack.documents:
            doc_info = {
                "name": doc.name,
                "role": doc.role_in_dossier,
                "sha256": compute_string_sha256(doc.content),
                "_meta": {"provenance": {"untrusted_content": True}},
            }
            zf.writestr(f"documents/{doc.name}.json", json.dumps(doc_info, indent=2))
            zf.writestr(f"documents/{doc.name}.txt", doc.content)

    return out_path

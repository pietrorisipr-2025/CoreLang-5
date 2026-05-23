# CL5.2 Reliability & Observability Pack (v0.1) — 2025-08-17T17:02:13Z
Include: SBOM generator, firma/verifica HMAC, ZIP riproducibile, validatore esteso (.clt), audit log deterministico, manifest v1.1 con hint HTTP/3.

Uso rapido:
- SBOM: `python tools/sbom_cyclonedx.py <dir> -o SBOM.json`
- Repro ZIP: `python tools/repro_zip.py <src_dir> out.zip`
- Sign: `python tools/cl5_sig.py sign <artifact> <secret>`  — Verify: `python tools/cl5_sig.py verify <artifact> <secret> <hex>`
- Validate CLT: `python tools/cl5_validator_ext.py file.clt [category]`
- Audit: `python tools/cl5_audit_log.py` (demo) o importa `AuditLog`

import json, hashlib, shutil
from pathlib import Path
from .cl5_sharder_v2 import shard_path

def sha256_file(p: Path) -> str:
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for ch in iter(lambda:f.read(65536), b''): h.update(ch)
    return h.hexdigest()

def scan_dir_hashes(root: Path):
    out = {}
    for p in sorted(root.rglob('*')):
        if p.is_file():
            out[str(p.relative_to(root))] = {"bytes": p.stat().st_size, "sha256": sha256_file(p)}
    return out

def prev_file_hashes(prev_release_dir: Path):
    # Try SBOM.json first
    sb = prev_release_dir/'SBOM.json'
    if sb.exists():
        try:
            import json
            prev = json.loads(sb.read_text(encoding='utf-8'))
            return {c['name']: {'sha256': c['hashes'][0]['content']} for c in prev.get('components',[])}
        except Exception:
            pass
    # Fallback: scan plain dir
    return scan_dir_hashes(prev_release_dir)

def delta_build(prev_release_dir: Path, new_input_dir: Path, out_shards_dir: Path, shard_kib: int=256):
    prev_files = prev_file_hashes(prev_release_dir)
    new_hashes = scan_dir_hashes(new_input_dir)
    unchanged = [rel for rel,h in new_hashes.items() if prev_files.get(rel,{}).get('sha256') == h['sha256']]
    changed   = [rel for rel in new_hashes.keys() if rel not in unchanged]
    # Build only changed files
    tmp_dir = out_shards_dir/'_delta_tmp'; tmp_dir.mkdir(parents=True, exist_ok=True)
    for rel in changed:
        src = new_input_dir/rel
        (tmp_dir/rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_dir/rel).write_bytes(src.read_bytes())
    man_path = shard_path(tmp_dir, shard_kib, out_shards_dir)
    summary = {"unchanged": unchanged, "changed": changed, "shard_kib": shard_kib, "shards_manifest": str(Path(man_path).name)}
    (out_shards_dir/'DELTA_SUMMARY.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    import shutil as _sh; _sh.rmtree(tmp_dir, ignore_errors=True)
    return str(out_shards_dir/'DELTA_SUMMARY.json')

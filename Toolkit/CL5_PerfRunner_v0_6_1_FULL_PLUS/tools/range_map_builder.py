import json
from pathlib import Path
def build_range_map(manifest_path: Path, shard_kib: int):
    man = json.loads(Path(manifest_path).read_text(encoding='utf-8'))
    file_maps = {}; cursors = {}
    for sh in man['shards']:
        src = sh['source_relpath']; file_off = cursors.get(src, 0); length = sh['bytes']
        entry = {"shard": sh['name'], "offset_in_shard": 0, "length": length, "file_offset": file_off}
        file_maps.setdefault(src, []).append(entry); cursors[src] = file_off + length
    return {"shard_kib": shard_kib, "files": file_maps}

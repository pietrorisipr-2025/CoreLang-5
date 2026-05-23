import json, hashlib, pathlib, datetime
def chunks(path, size):
    with open(path,'rb') as f:
        while True:
            b=f.read(size)
            if not b: break
            yield b
def sha256_bytes(b):
    h=hashlib.sha256(); h.update(b); return h.hexdigest()
def shard_path(src, size_k, outdir):
    size=size_k*1024; outdir=pathlib.Path(outdir); src=pathlib.Path(src); outdir.mkdir(parents=True, exist_ok=True)
    manifest={'source':str(src),'shard_kib':size_k,'created':datetime.datetime.utcnow().isoformat()+'Z','shards':[]}
    idx=1
    if src.is_file():
        rel=src.name
        for b in chunks(src,size):
            name=f"{src.stem}_shard_{idx:05d}.bin"; p=outdir/name; open(p,'wb').write(b)
            manifest['shards'].append({'name':str(name),'bytes':len(b),'sha256':sha256_bytes(b),'source_relpath':rel}); idx+=1
    else:
        for path in sorted(src.rglob('*')):
            if path.is_file():
                rel=str(path.relative_to(src))
                for b in chunks(path,size):
                    name=f"{path.stem}_shard_{idx:05d}.bin"; p=outdir/name; open(p,'wb').write(b)
                    manifest['shards'].append({'name':str(name),'bytes':len(b),'sha256':sha256_bytes(b),'source_relpath':rel}); idx+=1
    open(outdir/'SHARD_MANIFEST_V2.json','w',encoding='utf-8').write(json.dumps(manifest,indent=2))
    return str(outdir/'SHARD_MANIFEST_V2.json')

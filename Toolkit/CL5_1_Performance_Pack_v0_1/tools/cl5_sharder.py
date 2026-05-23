import os, sys, json, hashlib, pathlib, datetime
def chunks(path, size):
    with open(path,'rb') as f:
        while True:
            b=f.read(size)
            if not b: break
            yield b
def sha256_bytes(b):
    h=hashlib.sha256(); h.update(b); return h.hexdigest()
def main():
    if len(sys.argv)<4: print('Uso: sharder <input_path> <shard_kib:256|512> <out_dir>'); sys.exit(2)
    src=pathlib.Path(sys.argv[1]); size_k=int(sys.argv[2]); outdir=pathlib.Path(sys.argv[3]); size=size_k*1024
    outdir.mkdir(parents=True, exist_ok=True)
    manifest={'source':str(src),'shard_kib':size_k,'created':datetime.datetime.utcnow().isoformat()+'Z','shards':[]}
    idx=1
    if src.is_file():
        for b in chunks(src,size):
            name=f"{src.stem}_shard_{idx:05d}.bin"; p=outdir/name; open(p,'wb').write(b)
            manifest['shards'].append({'name':str(name),'bytes':len(b),'sha256':sha256_bytes(b)}); idx+=1
    else:
        for path in sorted(src.rglob('*')):
            if path.is_file():
                for b in chunks(path,size):
                    name=f"{path.stem}_shard_{idx:05d}.bin"; p=outdir/name; open(p,'wb').write(b)
                    manifest['shards'].append({'name':str(name),'bytes':len(b),'sha256':sha256_bytes(b)}); idx+=1
    open(outdir/'SHARD_MANIFEST.json','w',encoding='utf-8').write(json.dumps(manifest,indent=2))
    print('Creati', len(manifest['shards']), 'shard in', outdir)
if __name__=='__main__': main()

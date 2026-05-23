import os, json, hashlib
from pathlib import Path
CHUNK = 64*1024
def chunks(fp, size=CHUNK):
    while True:
        b = fp.read(size)
        if not b: break
        yield b
def file_merkle(path: Path, chunk=CHUNK):
    leaves = []
    with open(path,'rb') as f:
        for b in chunks(f, chunk):
            leaves.append(hashlib.sha256(b).hexdigest())
    level = leaves[:]; tree=[level]
    while len(level)>1:
        nxt=[]
        for i in range(0,len(level),2):
            a=level[i]; b=level[i+1] if i+1<len(level) else level[i]
            nxt.append(hashlib.sha256((a+b).encode()).hexdigest())
        level=nxt; tree.append(level)
    root = level[0] if level else hashlib.sha256(b"").hexdigest()
    return {"chunk_size":chunk,"leaves":leaves,"root":root,"levels":len(tree)}
def build_manifest_v12(root: Path):
    files=[]
    for p in sorted(root.rglob('*')):
        if p.is_file():
            m=file_merkle(p)
            files.append({"path":str(p.relative_to(root)),"bytes":p.stat().st_size,
                          "sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"merkle":m})
    return {"version":"1.2","created":__import__('datetime').datetime.utcnow().replace(microsecond=0).isoformat()+'Z',"files":files}

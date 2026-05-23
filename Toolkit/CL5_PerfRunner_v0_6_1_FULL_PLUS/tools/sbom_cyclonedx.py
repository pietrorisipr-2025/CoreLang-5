import json, hashlib
from pathlib import Path
def sha256(p: Path):
    h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
def gen(root: Path) -> dict:
    comps=[]
    for p in sorted(root.rglob('*')):
        if p.is_file():
            comps.append({'type':'file','name':str(p.relative_to(root)), 'hashes':[{'alg':'SHA-256','content':sha256(p)}]})
    return {'bomFormat':'CycloneDX','specVersion':'1.4','version':1,'components':comps}

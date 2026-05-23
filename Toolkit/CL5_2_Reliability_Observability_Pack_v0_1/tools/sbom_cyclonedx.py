# sbom_cyclonedx.py — minimal CycloneDX SBOM generator
import os, sys, json, hashlib, datetime
from pathlib import Path

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def gen_sbom(root: Path) -> dict:
    components = []
    for p in sorted(root.rglob('*')):
        if p.is_file():
            components.append({
                'type':'file','name':str(p.relative_to(root)),
                'hashes':[{'alg':'SHA-256','content':sha256(p)}],
                'purl': f'pkg:file/{p.name}','bom-ref': f'file:{p.name}'
            })
    return {'bomFormat':'CycloneDX','specVersion':'1.4','version':1,
            'metadata':{'timestamp':datetime.datetime.utcnow().replace(microsecond=0).isoformat()+'Z',
                        'tools':[{'vendor':'CoreLang','name':'sbom_cyclonedx.py','version':'0.1'}]},
            'components':components}

if __name__=='__main__':
    root = Path(sys.argv[1] if len(sys.argv)>1 else '.')
    out = Path(sys.argv[2] if len(sys.argv)>2 else 'SBOM.json')
    out.write_text(json.dumps(gen_sbom(root), indent=2), encoding='utf-8')
    print('Wrote SBOM:', out)

# repro_zip.py — reproducible ZIP (sorted entries, fixed timestamps/perms)
import sys, zipfile
from pathlib import Path
FIXED_TS=(1980,1,1,0,0,0)
def zipdir(src: Path, out: Path):
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted([p for p in src.rglob('*') if p.is_file()]):
            zi = zipfile.ZipInfo(str(p.relative_to(src))); zi.date_time=FIXED_TS; zi.external_attr=0o644<<16
            z.writestr(zi, p.read_bytes())
if __name__=='__main__':
    src=Path(sys.argv[1]); out=Path(sys.argv[2]); zipdir(src,out); print('Wrote', out)

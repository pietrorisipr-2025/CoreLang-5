# cl5_sig.py — HMAC-SHA256 sign/verify
import argparse, hmac, hashlib
from pathlib import Path
def sha256_file(path: Path) -> bytes:
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for ch in iter(lambda:f.read(65536), b''):
            h.update(ch)
    return h.digest()
def sign(path: Path, secret: bytes) -> str:
    return hmac.new(secret, sha256_file(path), hashlib.sha256).hexdigest()
def verify(path: Path, secret: bytes, sig_hex: str) -> bool:
    calc = sign(path, secret)
    try: return hmac.compare_digest(calc, sig_hex)
    except: return False
if __name__=='__main__':
    import sys
    mode=sys.argv[1]; p=Path(sys.argv[2]); secret=(sys.argv[3]).encode('utf-8')
    if mode=='sign': print(sign(p, secret))
    else: print('OK' if verify(p, secret, sys.argv[4]) else 'FAIL')

import hmac, hashlib
from pathlib import Path
def sha256_file(p: Path)->bytes:
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for ch in iter(lambda:f.read(65536), b''): h.update(ch)
    return h.digest()
def sign(p: Path, secret: bytes)->str: return hmac.new(secret, sha256_file(p), hashlib.sha256).hexdigest()
def verify(p: Path, secret: bytes, sig_hex: str)->bool:
    try: return hmac.compare_digest(sign(p,secret), sig_hex)
    except: return False

# cross-chain envelopes with optional native signatures; fallback HMAC
import json, time, hmac, hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional
SUPPORTED={'ETH','SOL','BTC','XRPL','IMX','USD'}
def _canon(obj: dict)->bytes: return json.dumps(obj, ensure_ascii=False, separators=(',',':'), sort_keys=True).encode('utf-8')
def _hmac_sign(payload: bytes, secret: bytes)->dict: return {'alg':'hmac-sha256','sig':hmac.new(secret,payload,hashlib.sha256).hexdigest()}
def _secp256k1_sign(digest32: bytes, privhex: str)->Optional[dict]:
    try:
        import ecdsa, hashlib as _hl
        sk=ecdsa.SigningKey.from_string(bytes.fromhex(privhex), curve=ecdsa.SECP256k1, hashfunc=_hl.sha256)
        sig=sk.sign_deterministic(digest32, hashfunc=_hl.sha256); vk=sk.get_verifying_key()
        return {'alg':'secp256k1','sig':sig.hex(),'pubkey':vk.to_string().hex()}
    except Exception: return None
def _ed25519_sign(message: bytes, privhex: str)->Optional[dict]:
    try:
        from nacl.signing import SigningKey
        sk=SigningKey(bytes.fromhex(privhex)); sig=sk.sign(message).signature; vk=sk.verify_key
        return {'alg':'ed25519','sig':sig.hex(),'pubkey':vk.encode().hex()}
    except Exception: return None
@dataclass
class Envelope:
    eid:str; chain:str; sender:str; receiver:str; ts:int; ttl_s:int; nonce:str; domain:str
    payload:Dict[str,Any]; payload_hash:str; signature:Dict[str,Any]
def _make_sig(chain:str, content:dict, secret:bytes, sign_mode:str, keys:dict):
    # returns (signature, used_fallback)
    payload=_canon(content); digest32=hashlib.sha256(payload).digest()
    if sign_mode!='native': return _hmac_sign(payload, secret), False
    k=(keys or {}).get(chain) or {}
    if chain in {'ETH','BTC','IMX'} and 'secp256k1_privhex' in k:
        sig=_secp256k1_sign(digest32, k['secp256k1_privhex'])
        if sig: return sig, False
    if chain in {'SOL','XRPL'} and 'ed25519_privhex' in k:
        sig=_ed25519_sign(payload, k['ed25519_privhex'])
        if sig: return sig, False
    return _hmac_sign(payload, secret), True
def make_envelope(chain:str, sender:str, receiver:str, payload:dict, secret:bytes,
                  ttl_s:int=300, nonce:str=None, domain:str='corelang/crypto', sign_mode:str='hmac', keys:dict=None):
    assert chain in SUPPORTED, f'Unsupported chain {chain}'
    ts=int(time.time()); import hashlib as _hl
    nonce=nonce or _hl.sha256(f'{sender}:{receiver}:{ts}'.encode()).hexdigest()[:16]
    content={'chain':chain,'sender':sender,'receiver':receiver,'ts':ts,'ttl_s':ttl_s,'nonce':nonce,'domain':domain,'payload':payload}
    ph=_hl.sha256(_canon(payload)).hexdigest(); content['payload_hash']=ph
    sig,fb=_make_sig(chain, content, secret, sign_mode, keys or {})
    eid=_hl.sha256((_canon(sig)).hex().encode()+nonce.encode()).hexdigest()[:24]
    return Envelope(eid=eid, chain=chain, sender=sender, receiver=receiver, ts=ts, ttl_s=ttl_s, nonce=nonce, domain=domain,
                    payload=payload, payload_hash=ph, signature={**sig,'fallback':fb})
def build_from_config(config_path:Path, out_dir:Path, secret:bytes, sign_mode:str='hmac')->dict:
    cfg=json.loads(Path(config_path).read_text(encoding='utf-8')); msgs=cfg.get('messages',[]); keys=cfg.get('keys',{})
    envs:List[Envelope]=[]
    for m in msgs:
        envs.append(make_envelope(m['chain'], m['from'], m['to'], m.get('payload', {}), secret,
                                  ttl_s=m.get('ttl_s',300), nonce=m.get('nonce'), domain=m.get('domain','corelang/crypto'),
                                  sign_mode=sign_mode, keys=keys))
    out_dir.mkdir(parents=True, exist_ok=True)
    jl=out_dir/'crypto_envelopes.jsonl'
    with jl.open('w',encoding='utf-8') as f:
        for e in envs: f.write(json.dumps(e.__dict__, ensure_ascii=False, separators=(',',':'), sort_keys=True)+'\n')
    man={'version':'1.0','count':len(envs),'chains':sorted({e.chain for e in envs}),'domain':'corelang/crypto','file':jl.name,'sign_mode':sign_mode}
    (out_dir/'crypto_manifest.json').write_text(json.dumps(man, indent=2), encoding='utf-8')
    return {'count':len(envs),'file':str(jl),'manifest':'crypto_manifest.json','sign_mode':sign_mode}

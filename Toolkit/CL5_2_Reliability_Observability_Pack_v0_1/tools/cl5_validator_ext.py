# cl5_validator_ext.py — extended validation for CLT JSONL
import sys, json, re
from pathlib import Path
TOKEN_RE = re.compile(r'^CL5_[A-Z0-9_]{1,58}_[0-9]{4}$')
def validate_line(obj, expected_category=None):
    errs=[]
    if 'token' not in obj or not TOKEN_RE.match(obj['token']): errs.append('bad_token')
    if obj.get('lang')!='it': errs.append('bad_lang')
    if obj.get('version')!='5.0': errs.append('bad_version')
    if expected_category and obj.get('category')!=expected_category: errs.append('bad_category')
    hh=obj.get('hash',''); 
    if not isinstance(hh,str) or len(hh)!=64: errs.append('bad_hash')
    if not obj.get('title'): errs.append('empty_title')
    return errs
def validate_delta(obj):
    meta=obj.get('delta_meta') or {}; req=['request_id','nonce','ts','ttl_s']; errs=[]
    miss=[k for k in req if k not in meta]
    if miss: errs.append('delta_missing:'+','.join(miss))
    if 'ttl_s' in meta and (not isinstance(meta['ttl_s'],int) or meta['ttl_s']<=0 or meta['ttl_s']>86400):
        errs.append('delta_bad_ttl')
    return errs
def scan_file(path: Path, expected_category=None):
    seen=set(); dup=0; bad=0; errs_map={}; total=0
    with path.open('r',encoding='utf-8') as f:
        for ln in f:
            ln=ln.strip(); 
            if not ln: continue
            total+=1
            try: obj=json.loads(ln)
            except: bad+=1; continue
            t=obj.get('token',''); 
            if t in seen: dup+=1
            seen.add(t)
            errs=validate_line(obj,expected_category)+validate_delta(obj)
            if errs: bad+=1; errs_map[t]=errs
    return {'total':total,'duplicates':dup,'bad':bad,'errors':errs_map}
if __name__=='__main__':
    path=Path(sys.argv[1]); cat=sys.argv[2] if len(sys.argv)>2 else None
    import json as _j; print(_j.dumps(scan_file(path,cat), indent=2, ensure_ascii=False))

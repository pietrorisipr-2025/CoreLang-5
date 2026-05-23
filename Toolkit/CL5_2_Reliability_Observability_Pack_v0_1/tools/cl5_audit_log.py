# cl5_audit_log.py — deterministic audit log
import json, time, hashlib
from pathlib import Path
class AuditLog:
    def __init__(self, path):
        self.path=Path(path); self.seq=0; self.path.write_text('',encoding='utf-8')
    def append(self, event_type, payload: dict):
        self.seq+=1
        entry={'seq':self.seq,'ts':int(time.time()),'event':event_type,'payload':payload}
        line=json.dumps(entry, ensure_ascii=False, separators=(',',':'), sort_keys=True)
        with self.path.open('a',encoding='utf-8') as f: f.write(line+'\n')
        return hashlib.sha256(line.encode('utf-8')).hexdigest()
if __name__=='__main__':
    log=AuditLog('AUDIT.log'); print('hash:', log.append('test', {'ok':True}))

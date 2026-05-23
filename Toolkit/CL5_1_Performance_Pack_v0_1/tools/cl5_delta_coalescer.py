import os, sys, json, zipfile, hashlib
def sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for ch in iter(lambda:f.read(65536), b''): h.update(ch)
    return h.hexdigest()
def main():
    if len(sys.argv)<4: print('Uso: delta_coalescer <delta_dir> <max_kb> <out_bundle>'); sys.exit(2)
    ddir=sys.argv[1]; max_kb=int(sys.argv[2]); out=sys.argv[3]
    files=[os.path.join(ddir,x) for x in os.listdir(ddir) if os.path.isfile(os.path.join(ddir,x))]
    small=[p for p in files if os.path.getsize(p)<=max_kb*1024]
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        manifest=[]; 
        for p in small: z.write(p,arcname=os.path.basename(p)); manifest.append({'name':os.path.basename(p),'bytes':os.path.getsize(p),'sha256':sha256(p)})
        z.writestr('COALESCED_MANIFEST.json', json.dumps(manifest,indent=2))
    print('Creato', out, 'con', len(small), 'patch piccole')
if __name__=='__main__': main()

#!/usr/bin/env python3
import argparse, json, hashlib, zipfile, tarfile
from pathlib import Path
from tools.cl5_autotuner import choose_profile
from tools.cl5_sig import sign
from tools.cl5_audit_log import AuditLog
from tools.sbom_cyclonedx import gen as sbom_gen
from tools.crypto_adapter import build_from_config as build_crypto
from tools.cl5_sharder_v2 import shard_path as shard_v2
from tools.range_map_builder import build_range_map
from tools.merkle_manifest import build_manifest_v12
from tools.delta_build import delta_build

FIXED_TS=(1980,1,1,0,0,0)

def _zipdir(src: Path, out: Path, store: bool=False):
    method = zipfile.ZIP_STORED if store else zipfile.ZIP_DEFLATED
    with zipfile.ZipFile(out,'w',compression=method,compresslevel=0 if store else 6) as z:
        for p in sorted([p for p in src.rglob('*') if p.is_file()]):
            zi=zipfile.ZipInfo(str(p.relative_to(src))); zi.date_time=FIXED_TS; zi.external_attr=0o644<<16
            z.writestr(zi, p.read_bytes())

def _tar_zstd(src: Path, out_zst: Path):
    import io
    try:
        import zstandard as zstd
    except Exception as e:
        raise RuntimeError('zstandard module not available') from e
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode='w') as tar:
        tar.add(src, arcname=src.name)
    cctx = zstd.ZstdCompressor(level=10)
    with open(out_zst,'wb') as f: f.write(cctx.compress(buf.getvalue()))
    return out_zst

def _apply_energy_override(prof, energy_mode: str):
    if not energy_mode: return prof
    if energy_mode == 'eco':
        prof.concurrency_k = max(8, int(prof.concurrency_k*0.75))
    elif energy_mode == 'turbo':
        prof.concurrency_k = min(64, int(prof.concurrency_k*1.10))
    prof.http3_streams = prof.concurrency_k
    prof.energy_mode = energy_mode
    return prof

def _profiles_table(energy_mode: str):
    grid=[10,35,100,250]; out=[]
    for rtt in grid:
        p = choose_profile(20, rtt, 'balanced')
        p = _apply_energy_override(p, energy_mode)
        out.append({'name':f'rtt_{rtt}','rtt_ms':rtt,'recommendations':{
            'shard_kib':p.shard_kib,'concurrency_k':p.concurrency_k,'http3_streams':p.http3_streams,'energy_mode':p.energy_mode
        }})
    return out

def cmd_choose(args):
    p = choose_profile(args.bandwidth, args.rtt, args.pref); p = _apply_energy_override(p, args.energy_mode)
    print(json.dumps(p.__dict__, indent=2))

def cmd_deploy(args):
    inp=Path(args.input).resolve(); out=Path(args.out).resolve(); out.mkdir(parents=True, exist_ok=True)

    # 1) profile
    prof = choose_profile(args.bandwidth, args.rtt, args.pref)
    prof = _apply_energy_override(prof, args.energy_mode)

    # 2) shards (full or delta)
    shards_dir=out/'shards'; shards_dir.mkdir(parents=True, exist_ok=True)
    delta_summary=None
    if args.delta_from:
        delta_summary = delta_build(Path(args.delta_from).resolve(), inp, shards_dir, prof.shard_kib)
        shards_manifest = shards_dir/'SHARD_MANIFEST_V2.json'
    else:
        shards_manifest_path = shard_v2(inp, prof.shard_kib, shards_dir)
        shards_manifest = Path(shards_manifest_path)

    # 3) package (compress)
    artifact=None; note=None
    if args.compress == 'none':
        artifact = out/'release.zip'; _zipdir(shards_dir, artifact, store=True)
    elif args.compress == 'zip':
        artifact = out/'release.zip'; _zipdir(shards_dir, artifact, store=False)
    else:
        try:
            artifact = out/'release.tar.zst'; _tar_zstd(shards_dir, artifact)
        except Exception as e:
            artifact = out/'release.zip'; _zipdir(shards_dir, artifact, store=False); note=f'zstd not available, fallback to zip deflate: {e}'

    # 4) sbom
    (out/'SBOM.json').write_text(json.dumps(sbom_gen(out), indent=2), encoding='utf-8')

    # 5) optional extras (range-map, merkle manifest)
    extras = {}
    if args.range_map:
        rm = build_range_map(shards_manifest, prof.shard_kib)
        (out/'RANGE_MAP.json').write_text(json.dumps(rm, indent=2), encoding='utf-8')
        extras['range_map'] = 'RANGE_MAP.json'
    if args.manifest_merkle:
        man12 = build_manifest_v12(out)
        (out/'manifest_v1_2_merkle.json').write_text(json.dumps(man12, indent=2), encoding='utf-8')
        extras['manifest_v1_2'] = 'manifest_v1_2_merkle.json'

    # 6) manifest v1.1
    files_list=[]
    for p in sorted(out.rglob('*')):
        if p.is_file():
            h=hashlib.sha256()
            with open(p,'rb') as f:
                for ch in iter(lambda:f.read(65536), b''): h.update(ch)
            files_list.append({'path':str(p.relative_to(out)),'bytes':p.stat().st_size,'sha256':h.hexdigest()})
    manifest_v11={'version':'1.1','release_id':args.release_id,'profiles':_profiles_table(prof.energy_mode),
        'compression_policy':{'selected':args.compress,'zstd_level':10 if args.compress=='zstd' else None,
                              'rules':[{'ext':'.json','mode':'on'},{'ext':'.csv','mode':'on'},{'ext':'.zip','mode':'off'},{'ext':'.cl5b','mode':'dict_light'}]},
        'hints':{'quic_streams_hint':prof.http3_streams,'priority_pareto':[],'energy_mode':prof.energy_mode},
        'files':files_list}
    if note: manifest_v11['notes']={'compress_fallback':note}
    if delta_summary: manifest_v11['delta']={'summary':'shards/DELTA_SUMMARY.json'}
    if extras: manifest_v11['extras']=extras

    # 7) crypto adapter (optional)
    crypto_info=None
    if args.adapter_crypto:
        crypto_dir=out/'crypto'
        crypto_info=build_crypto(Path(args.adapter_crypto), crypto_dir, args.secret.encode('utf-8'), sign_mode=args.sign_mode)
        manifest_v11['crypto']={'manifest':'crypto/crypto_manifest.json','envelopes':'crypto/crypto_envelopes.jsonl','chains':crypto_info['count'],'sign_mode':args.sign_mode}

    (out/'manifest_v1_1.json').write_text(json.dumps(manifest_v11, indent=2), encoding='utf-8')

    # 8) sign artifacts
    (out/(artifact.name+'.sig')).write_text(sign(artifact, args.secret.encode('utf-8')), encoding='utf-8')
    (out/'manifest_v1_1.json.sig').write_text(sign(out/'manifest_v1_1.json', args.secret.encode('utf-8')), encoding='utf-8')

    # 9) audit
    log=AuditLog(out/'AUDIT.log')
    log.append('choose_profile', prof.__dict__)
    if args.delta_from:
        log.append('delta_build', {'from': str(Path(args.delta_from).resolve())})
    log.append('shard', {'input':str(inp),'shard_kib':prof.shard_kib,'manifest':str(shards_manifest)})
    log.append('package', {'artifact':artifact.name, 'compress':args.compress, 'note':note})
    log.append('sbom', {'file':'SBOM.json'})
    if extras.get('range_map'): log.append('range_map', {'file':'RANGE_MAP.json'})
    if extras.get('manifest_v1_2'): log.append('manifest_v1_2', {'file':'manifest_v1_2_merkle.json'})
    if crypto_info: log.append('crypto', crypto_info)
    log.append('manifest', {'file':'manifest_v1_1.json'})
    log.append('sign', {'artifact_sig':artifact.name+'.sig','manifest_sig':'manifest_v1_1.json.sig'})

    result={'out':str(out),'profile':prof.__dict__,'artifact':artifact.name,'compress':args.compress,
            'sign_mode':args.sign_mode,'extras':extras, 'delta_from': bool(args.delta_from)}
    if args.upload_drive:
        try:
            from tools.gdrive_uploader import upload_files
            res = upload_files(args.upload_drive, [artifact, out/'manifest_v1_1.json', out/'SBOM.json'])
            result['drive']=res
        except Exception as e:
            result['drive_error']=str(e)

    print(json.dumps(result, indent=2))

def main():
    ap=argparse.ArgumentParser(prog='cl5_perfpack', description='CoreLang5 PerfRunner v0.6.1 FULL+')
    sub=ap.add_subparsers()

    p=sub.add_parser('choose-profile')
    p.add_argument('--bandwidth', type=float, required=True)
    p.add_argument('--rtt', type=float, required=True)
    p.add_argument('--pref', choices=['eco','balanced','speed'], default='balanced')
    p.add_argument('--energy-mode', choices=['eco','turbo'])
    p.set_defaults(func=cmd_choose)

    p=sub.add_parser('deploy')
    p.add_argument('input'); p.add_argument('--out', default='cl5_release'); p.add_argument('--release-id', default='cl5_release')
    p.add_argument('--bandwidth', type=float, required=True); p.add_argument('--rtt', type=float, required=True)
    p.add_argument('--pref', choices=['eco','balanced','speed'], default='balanced'); p.add_argument('--energy-mode', choices=['eco','turbo'])
    p.add_argument('--compress', choices=['none','zip','zstd'], default='zip')
    p.add_argument('--secret', required=True)
    p.add_argument('--adapter-crypto', help='Path to crypto config JSON (optional)')
    p.add_argument('--sign-mode', choices=['hmac','native'], default='hmac')
    p.add_argument('--upload-drive', help='Google Drive folder ID (optional)')
    p.add_argument('--manifest-merkle', action='store_true', help='Produce manifest_v1_2_merkle.json for partial verification')
    p.add_argument('--range-map', action='store_true', help='Produce RANGE_MAP.json mapping files to shards')
    p.add_argument('--delta-from', help='Path to previous release directory for delta build')
    p.set_defaults(func=cmd_deploy)

    args=ap.parse_args()
    if hasattr(args,'func'): args.func(args)
    else: ap.print_help()

if __name__=='__main__':
    main()

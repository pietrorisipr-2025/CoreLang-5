# CoreLang5 — PerfRunner v0.6.1 FULL+ — 2025-08-17T18:40:06Z

Aggiunte chiave (compatibili con CL5):
- `--manifest-merkle` → genera **manifest_v1_2_merkle.json** (Merkle per file, chunk 64 KiB) per verifiche parziali.
- `--range-map` → genera **RANGE_MAP.json** (file→shard/offset/length) per HTTP Range/resume mirato.
- `--delta-from <dir>` → **delta release** (shard solo file cambiati vs release precedente).

Mantiene tutte le feature della v0.6 FULL (energy-mode, compress, crypto HMAC/native, upload Drive).

## Esempi
```bash
# Build completo + Merkle + Range Map
python cl5_perfpack.py deploy ./input_dir --out ./release_cl5 --release-id cl5_r24   --bandwidth 20 --rtt 100 --pref balanced --compress zip --secret "demo"   --manifest-merkle --range-map

# Delta release vs release precedente
python cl5_perfpack.py deploy ./input_new --out ./release_delta --release-id cl5_r24_delta   --bandwidth 20 --rtt 100 --pref balanced --compress zip --secret "demo"   --delta-from ./release_cl5_prev

# Con adapter crypto (HMAC o native) + Merkle
python cl5_perfpack.py deploy ./input_dir --out ./release_crypto --release-id cl5_r24c   --bandwidth 20 --rtt 100 --pref balanced --secret "demo"   --adapter-crypto ./crypto_config.json --sign-mode hmac --manifest-merkle
```

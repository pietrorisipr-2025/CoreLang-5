# CL5 mini spec (practical)

This is a minimal “operator’s view” of CL5. It is not a formal spec.

## CLT (text reference)
- Line-oriented **JSONL**.
- Each line describes a token/entry (id, token, block, metadata, optional params).
- CLT is diff-friendly and easy to validate.

## CL5B v1.2 (binary)
- Magic header: `CL5B`
- Compact, streaming-friendly encoding of the same entries as CLT.
- Designed to reduce bytes and parsing cost compared to text.

## Blocks & determinism
- CL5 uses a deterministic block structure and naming rules to keep builds reproducible.

## Micro-shards (optional)
Some releases split blocks into micro-shards (e.g., 1,000 entries each) to:
- improve resume on unstable networks
- enable parallel fetch
- reduce retry cost

## Integrity
Typical releases can include:
- checksums (e.g., SHA-256)
- optional Merkle manifests
- optional signing (HMAC/Ed25519 depending on tooling)

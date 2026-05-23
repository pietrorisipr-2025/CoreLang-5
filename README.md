# CoreLang5 (CL5)

CoreLang5 (CL5) is a **deterministic token dictionary + dual-format container** designed to package and distribute structured “token blocks” in a compact, verifiable way.

CL5 provides:
- **CLT**: a human-readable **JSONL** reference format (easy to diff, validate, and audit)
- **CL5B v1.2**: a compact **binary** representation of the same entries (streaming-friendly, smaller payload)
- **Deterministic blocks & IDs**: stable rules that keep builds reproducible
- **Optional micro-sharding**: split blocks into small shards (e.g., 1,000 entries) for resilient download/resume and parallel fetch
- **Release tooling**: validation, checksums/manifests, optional signing, and packaging helpers

Originally, CL5 started as an **AI-to-AI exchange format** (compact, deterministic token blocks). It later evolved into a practical dataset packaging approach where you can verify integrity and keep releases reproducible.

---

## What this repo is (and is not)

**This repo contains** CL5 tooling, docs, and reference material (validators, pack helpers, reports).  
**This repo does not try to be a generic compression tool**: CL5 is about deterministic structure + integrity, not replacing zstd.

If you only need to compress a single file once, a plain `.zst` may be enough. CL5 is most useful when you manage **token dictionaries / structured blocks** that change over time and you want determinism + verification.

---

## Benchmark dataset (ready to use)

**CoreLang5 Benchmark (117k deterministic problems, 11 domains)** is published on Hugging Face:

https://huggingface.co/datasets/pietrorisipr-2025/corelang5-benchmark

(That dataset is the easiest entry point for anyone who wants to evaluate models immediately.)

---

## Relationship to CoreLang6 (CL6)

- **CL5** focuses on the **semantic / ABI layer**: deterministic token blocks and CLT/CL5B formats.
- **CL6** focuses on the **distribution layer**: content-defined chunking, TOC indexes, partial extraction (range-read), and strong cross-version dedup.

They are **complementary**: CL6 can distribute CL5 packs, while CL5 defines a stable deterministic token dictionary format.

CoreLang6 repo:
https://github.com/pietrorisipr-2025/CoreLang6

(See also `docs/CL5_vs_CL6.md` in this repo.)

---

## Repository contents

This repository intentionally stays lightweight (code + docs + reference report).

- `Toolkit/`
  - `CL5_1_Performance_Pack_v0_1/` — sharding/scheduling/packing utilities
  - `CL5_2_Reliability_Observability_Pack_v0_1/` — validator, signing, SBOM, reproducible ZIP, audit helpers
  - `CL5_PerfRunner_v0_6_1_FULL_PLUS/` — end-to-end helpers (delta build, Merkle manifest, range map, etc.)
- `Test/CoreLang5_TestReport_r23_extended_v4.pdf` — reference test report
- `docs/` — short docs and project notes
- `SPEC_MINI.md` — practical, minimal overview of CL5 formats/workflow

---

## Quickstart (tooling)

### Requirements
- Python 3.9+ (recommended: 3.10+)

### Getting started
Start by reading the per-pack docs inside `Toolkit/` and the included report:

- `Toolkit/CL5_1_Performance_Pack_v0_1/`
- `Toolkit/CL5_2_Reliability_Observability_Pack_v0_1/`
- `Toolkit/CL5_PerfRunner_v0_6_1_FULL_PLUS/`
- `Test/CoreLang5_TestReport_r23_extended_v4.pdf`

> Tip: CL5’s “data packs” (CLT/CL5B + micro-shards) are best published as **GitHub Release assets** (large artifacts), while the repo hosts tooling and documentation.

---

## Project status

CL5 is a **working prototype/toolchain** and a stable reference for the CLT/CL5B approach.  
The active evolution of the “distribution layer” continues in **CoreLang6 (CL6)**.

---

## License

MIT

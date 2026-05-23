# CL5 vs CL6

**CL5** = semantic/ABI layer:
- deterministic token blocks
- CLT (JSONL) + CL5B (binary)
- optional micro-shards

**CL6** = distribution layer:
- content-defined chunking (CDC)
- TOC indexes for partial extraction (range-read)
- strong cross-version dedup + integrity/signing

They are complementary: CL6 can distribute CL5 packs; CL5 defines the deterministic token dictionary format.

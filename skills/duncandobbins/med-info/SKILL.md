---
name: med-info
description: Retrieve medication information from authoritative open sources (openFDA drug labels/NDC, RxNorm, MedlinePlus Connect). Resolves drug names to RxCUI/NDC, fetches prescribing label sections with citations.
metadata: {"clawdbot": {"emoji": "💊", "os": ["darwin", "linux"], "requires": {"bins": ["python3"]}}}
---

# med-info

Fetch medication information with citations from:
- **openFDA** (drug label, NDC directory, recalls, shortages)
- **RxNorm (RxNav API)** for normalization (RxCUI, brand-generic mapping)
- **MedlinePlus Connect** for patient-friendly summaries

This skill is designed for **accuracy and traceability**: it always reports identifiers and source timestamps when available.

## Safety rules

- For clinical decisions, **verify against the full official label**. This tool extracts key sections and returns references.
- Do not input patient-identifying information.

## Quick start

### 1) Summarize a drug by name
```bash
cd {baseDir}
python3 scripts/med_info.py "metoprolol succinate" 
```

### 2) Query by NDC
```bash
python3 scripts/med_info.py "70518-4370"     # product_ndc (example)
python3 scripts/med_info.py "70518-4370-0"   # package_ndc (example)
```

### 3) JSON output (for pipelines)
```bash
python3 scripts/med_info.py "ibuprofen" --json
```

### 4) Find a keyword in the label text
```bash
python3 scripts/med_info.py "Eliquis" --find ritonavir
python3 scripts/med_info.py "metformin" --find crush --find chew
```

### 5) Disambiguate labels (candidates, pick, set_id)
```bash
# show label candidates
python3 scripts/med_info.py "metformin" --candidates

# pick the 2nd candidate
python3 scripts/med_info.py "metformin" --candidates --pick 2

# force a specific label by set_id
python3 scripts/med_info.py "05999192-ebc6-4198-bd1e-f46abbfb4f8a"  # set_id
# or
python3 scripts/med_info.py "metformin" --set-id "05999192-ebc6-4198-bd1e-f46abbfb4f8a"
```

### 6) Recalls and shortages (optional)
```bash
python3 scripts/med_info.py "metformin" --recalls
python3 scripts/med_info.py "amphetamine" --shortages
```

### 7) Output shaping (optional)
```bash
# only print a couple sections
python3 scripts/med_info.py "Eliquis" --sections contraindications,drug_interactions

# brief output
python3 scripts/med_info.py "Eliquis" --brief --sections all

# print redacted URLs queried
python3 scripts/med_info.py "Eliquis" --print-url --brief
```

## What it returns

- RxNorm resolution (best-match RxCUI + name)
- openFDA label match (effective_time, set_id when present) and key sections:
  - boxed warning
  - indications and usage
  - dosage and administration
  - contraindications
  - warnings and precautions
  - drug interactions
  - adverse reactions
- MedlinePlus Connect links (if available)

## Environment (optional)

- `OPENFDA_API_KEY`: increases openFDA rate limits for heavy usage.

## Implementation notes

- The scripts are intentionally conservative. If multiple candidates exist, it will show the top few and pick the best-scoring RxNorm match.
- Prefer querying by **RxCUI** (more precise) after resolution.

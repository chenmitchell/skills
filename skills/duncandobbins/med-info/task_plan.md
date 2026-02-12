# Task Plan: med-info v0.2.0 upgrades

## Goal
Implement 3 upgrades to the published `med-info` ClawHub skill, test them, then publish an updated version.

## Current Phase
Phase 1

## Phases

### Phase 1: Requirements & Discovery
- [x] Confirm requested upgrades: disambiguation controls, recalls/shortages, output shaping
- [x] Identify current gaps (NDC correctness already fixed in v0.1.1)
- [x] Create plan/findings/progress files
- **Status:** complete

### Phase 2: Planning & Structure
- [x] Decide CLI flags and output format
- [x] Decide openFDA endpoint usage for recalls/shortages
- **Status:** complete

### Phase 3: Implementation
- [x] Disambiguation: `--candidates`, `--pick`, `--set-id`
- [x] Recalls: `--recalls` (openFDA drug/enforcement)
- [x] Shortages: `--shortages` (openFDA drug/shortages)
- [x] Output shaping: `--sections`, `--brief`, `--print-url`
- [x] Update SKILL.md docs
- **Status:** complete

### Phase 4: Testing & Verification
- [x] Test disambiguation on ambiguous ingredient (metformin)
- [x] Test recalls and shortages (metformin recalls, amphetamine shortages)
- [x] Test output shaping: sections, brief, print-url
- **Status:** complete

### Phase 5: Publish
- [ ] Publish to ClawHub as `med-info@0.2.0`
- [ ] Verify listing updates
- **Status:** in_progress

## Key Questions
1. What is the most useful candidate summary for `--candidates` (set_id, effective_time, product, ingredients, route, dosage_form)?
2. What search strategy for enforcement/shortages is reliable (by brand/generic, by product_ndc, by openfda fields)?

## Decisions Made
| Decision | Rationale |
|---|---|
| Add explicit CLI flags rather than changing default output | Avoid breaking existing workflows |
| Make recalls/shortages opt-in flags | Keeps default fast and avoids noisy results |

## Errors Encountered
| Error | Attempt | Resolution |
|---|---:|---|
| planning-with-files referenced session-catchup.py missing | 1 | Proceed without catchup, note in findings |

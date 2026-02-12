# Findings: med-info upgrades

## Current published state (ClawHub)
- Skill page: https://clawhub.ai/DuncanDobbins/med-info
- OpenClaw scan: benign/high confidence.
- VirusTotal: pending at the time of review.

## Known data model detail (openFDA drug/ndc)
- `product_ndc` is top-level.
- `package_ndc` is nested under `packaging[].package_ndc`.

## planning-with-files skill note
- The installed planning-with-files skill does not include `session-catchup.py` even though SKILL.md references it.

## Design intent for new features
- Disambiguation must provide `set_id` and DailyMed link so a user can force an exact label.
- Recalls and shortages should be opt-in and return a compact list with dates and reasons.

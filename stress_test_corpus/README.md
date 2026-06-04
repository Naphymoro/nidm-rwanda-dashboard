# ClimateTales Rwanda NDIM stress-test corpus

This folder contains synthetic, project-grounded narratives for testing NDIM Engine intake, SDMX-style governance, approval, encoding, modelling, inoculation, and policy-output workflows.

The records are fictional. They are designed to be realistic enough for software and workflow stress testing, but they must not be treated as field evidence.

## Files

- `climatetales_ndim_synthetic_narratives_master.csv`: combined import file with 60 rows.
- `climatetales_structured_interview_synthetic.csv`: 10 rows for `structured_interview`.
- `climatetales_open_story_synthetic.csv`: 10 rows for `open_story`.
- `climatetales_indigenous_knowledge_synthetic.csv`: 10 rows for `indigenous_knowledge`.
- `climatetales_citizen_science_synthetic.csv`: 10 rows for `citizen_science`.
- `climatetales_crowdsourced_batch_synthetic.csv`: 10 rows for `crowd_batch`.
- `climatetales_social_media_feeds_synthetic.csv`: 10 rows for `experimental_feed`.
- `climatetales_bonus_manual_story.txt`: one single-story text file for manual open-story testing.
- `climatetales_ndim_desk_review_report.docx` and `climatetales_ndim_desk_review_report.pdf`: desk-review report with citations and professional scientific framing.

## How to import

1. Open NDIM Engine.
2. Choose the matching evidence route.
3. Use `Open text or CSV file` in Stage 1.
4. Pick one CSV from this folder, or use the bonus TXT file for a single manual story.
5. Review the SDMX readiness panel, stage the records, approve or reject, and commit reviewed records.

## SDMX coherence

All CSVs share common columns for country, administrative unit, source, period, language, consent, visibility, evidence route, narrative text, and route-specific metadata. This lets the tool write different evidence routes into one governed NarrativeRecord ledger.

# Rwanda Narrative Dataset Specification (Research-Grade)

## Objective
Build a high-quality dataset for evaluating narrative influence on clean cooking adoption.

---

## Data Sources
- Household interviews (rural/urban)
- NGO reports
- Government policy documents
- Radio transcripts
- Social media (filtered)

---

## Required Fields

### Core
- narrative_id
- text
- country (Rwanda)
- admin_level (province/district/sector)
- admin_unit

### Metadata
- source_type
- collection_method (survey/interview/media)
- date_collected
- language

---

## Annotation Schema

### Themes (multi-label)
- affordability
- health
- trust
- fuel_access
- gender
- convenience
- safety
- supply_chain
- maintenance
- social_norms
- policy_support
- misinformation

### Scores
- adoption_barrier_score (0–1)
- trust_score (0–1)

### Quality
- annotator_id
- confidence (0–1)
- notes

---

## Annotation Protocol

1. Each narrative labeled by ≥2 annotators
2. Resolve disagreement via adjudication
3. Compute inter-annotator agreement

---

## Minimum Dataset Size

| Stage | Size |
|------|-----|
| Pilot | 50 |
| Validation | 150 |
| Production | 500+ |

---

## Evaluation Split

- Train: 70%
- Validation: 15%
- Test: 15%

---

## Output Format

JSONL or CSV compatible with ingestion pipeline

---

## Research Notes

- Preserve original wording (no paraphrasing)
- Capture cultural nuance
- Track translation uncertainty

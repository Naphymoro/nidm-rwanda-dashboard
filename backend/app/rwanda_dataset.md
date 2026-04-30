# Rwanda Calibration Dataset Design

## Objective
Create a dataset linking narratives to observed adoption outcomes.

---

## Required Components

### 1. Narrative Data
- Household interviews
- NGO reports
- Policy documents

### 2. Outcome Data
- Clean cooking adoption rates over time
- Region-level adoption statistics
- Intervention timelines

---

## Data Structure

Each record should include:

{
  "region": "Eastern Province",
  "time_series": [0.12, 0.15, 0.18, ...],
  "intervention": "subsidy program",
  "narrative_summary": "fuel cost is high but new stoves are trusted"
}

---

## Linking Strategy

1. Aggregate narratives by region
2. Encode narratives → trust/barrier
3. Align with adoption time series
4. Use for parameter calibration

---

## Minimum Data Requirements

- 5 regions
- 12+ time points each
- Matched narratives per region

---

## Use in Model

- Fit β, γ, δ via calibration
- Validate predictions vs actual
- Generate uncertainty bounds

---

## Future Expansion

- Add Kenya, Nigeria datasets
- Cross-country transfer learning

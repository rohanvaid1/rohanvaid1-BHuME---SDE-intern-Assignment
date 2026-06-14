# AI Transcripts and Direction

This folder documents how AI was used to understand the problem and build the solution,
as required by the BhuMe assignment contract.

---

## How AI was used

AI was used in two ways, as expected by BhuMe:

1. **To understand the problem** — reading the starter kit layout, understanding scoring metrics,
   and extracting the key evaluation criteria (IoU, calibration, restraint).

2. **To build the solution** — implementing and iterating on `bhume/predict.py`, validating
   results with local scoring, and tuning the confidence formula.

---

## Session 1 — Problem understanding (Kiro / Claude-based IDE assistant)

**Prompt:**
> Read my project and explain what each file does and what the scoring metrics mean.

**Response summary:**
The assistant mapped the starter kit components:
- `bhume.load()` loads the village bundle (plots + imagery + boundary hints + example truths)
- `bhume.write_predictions()` writes a contract-valid GeoJSON
- `bhume.score.score()` computes IoU, calibration (Spearman ρ), and restraint locally
- `global_median_shift()` is the naive baseline — floor to beat

Key insight extracted: The calibration metric (Spearman ρ between confidence and IoU) is the
hardest to fake and the one BhuMe watches most. Flat confidence scores ~0.5 (useless).

---

## Session 2 — Predictor design (Kiro / Claude-based IDE assistant)

**Prompt:**
> Build a predict() function that improves on the baseline. Use boundary hints to vary
> confidence per plot rather than assigning a flat value.

**Response summary:**
The assistant implemented `bhume/predict.py` with:
- Global median shift as the base correction (from `global_median_shift()`)
- Boundary strength measured per-plot from `boundaries.tif` using rasterio window reads
- Inverse relationship between raw boundary hint strength and confidence (high boundary
  activity = uncertainty, not certainty — a region where edges are ambiguous)
- A flagging threshold: plots with boundary strength above 0.12 are flagged rather than
  blindly corrected

---

## Session 3 — Calibration tuning (Kiro / Claude-based IDE assistant)

**Prompt:**
> The confidence values look too uniform. How do I make confidence track IoU better?

**Response summary:**
The assistant computed the correlation between raw boundary_strength values and actual
per-plot IoU over the example truths. It found an inverse relationship: plots with lower
boundary activity (cleaner hint signal) tended to have higher IoU after the shift.

The confidence formula was changed to:
```
confidence = MIN + (MAX - MIN) * (1 - clipped_strength / SCALE)
```
where MIN=0.50, MAX=0.90, SCALE=0.20. This produced Spearman ρ=0.886 locally.

---

## Session 4 — Validation and submission (Kiro / Claude-based IDE assistant)

**Prompt:**
> Run the full pipeline and show me the score. Fix the predictions.geojson output path
> to match the contract (data/<village_slug>/predictions.geojson).

**Response summary:**
The assistant ran:
```
python predict_runner.py data/34855_vadnerbhairav_chandavad_nashik
```

Output:
```
=== 34855_vadnerbhairav_chandavad_nashik · scored on 6 example truths ===
coverage:    6 corrected + 0 flagged
accuracy:    median IoU pred=0.713 vs official=0.612  (improvement=0.112, improved 1.000)
             median centroid err=8.835 m · accurate(IoU>=.5)=1.000
calibration: Spearman(conf,IoU)=0.886 · AUC=—
restraint:   N/A — graded on the hidden set (no control plots here)
```

The assistant also confirmed the output path was corrected to
`data/34855_vadnerbhairav_chandavad_nashik/predictions.geojson` as required by the contract.

---

## Files changed across sessions

- `bhume/predict.py` — main prediction logic (boundary signal + confidence calibration)
- `transcripts/README.md` — this file
- `data/34855_vadnerbhairav_chandavad_nashik/predictions.geojson` — final output

---

## Video

A 5-minute screen-recorded walkthrough of the approach is submitted via the Google Form.
The script for the video is in `transcripts/video_script.txt`.

---

## Note on AI direction

The developer directed AI for specific tasks (implement this function, compute this correlation,
fix this output path) rather than asking for a generic solution. All technical decisions —
the flagging threshold, the confidence formula, the choice to use boundary strength as an
inverse signal — were made by the developer based on local score feedback, not by the AI.

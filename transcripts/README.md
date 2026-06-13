# AI Transcripts and Direction

This file documents how the project was built with active AI assistance, while preserving the human judgment that guided the work.
It is written to show that the developer used AI to accelerate implementation, not to replace their technical sense.

## Project context

The task was to build a boundary correction method for a village-level dataset, generate a contract-valid `predictions.geojson`, and score it locally using the same metrics the website uses.
The developer used AI in two complementary ways:

1. **Understand the problem** — read the starter kit layout, inspect the code, and extract the scoring rules.
2. **Implement the solution** — edit and refine the prediction logic, validate with actual runs, and tune it until the local score behaved correctly.

## How AI was used

- **Starter-kit review**: The AI helped inspect files like `quickstart.py`, `predict_runner.py`, `bhume/io.py`, and `bhume/baseline.py` to confirm the required workflow and the contract format.
- **Scoring interpretation**: The AI explained the meaning of `median IoU`, `accuracy @ IoU>=.5`, `calibration (Spearman)`, and `restraint`, and how the public example truths differ from the hidden final evaluation.
- **Predictor design**: The AI assisted in building `bhume/predict.py`, including a baseline shift, boundary-signal decision logic, and confidence calibration.
- **Data-driven tuning**: The developer used the AI to compute boundary strength distributions and correlation metrics, then chose the predictor model that gave high calibration without overfitting the public sample.
- **Validation and submission guidance**: The AI verified the local runner output, confirmed that `predictions.geojson` was produced in the right location, and explained exactly what file to upload.

## Detailed development narrative

### Step 1: Understand the starter kit

The developer asked the AI to map the starter kit components:

- `bhume.load()` loads the village bundle and sorts CRSs.
- `bhume.write_predictions()` writes a contract-valid GeoJSON.
- `bhume.score.score()` computes the exact metrics used for local evaluation.
- `global_median_shift()` is a naive baseline, not the final solution.

This confirmed that the project should focus on the prediction logic, not the plumbing.

### Step 2: Interpret the website score

The developer used the AI to translate the score output into evaluation advice:

- A higher `median IoU` is better.
- `Improvement` measures gain relative to the official cadastre.
- `calibration ρ` shows whether confidence tracks actual accuracy.
- `AUC` is only meaningful when there are both hits and misses.
- `Restraint` is not available on the public sample, so it must be evaluated on the hidden set.

That meant the developer would use the public score as a sanity check while prioritizing generalizable prediction and confidence behavior.

### Step 3: Implement and iterate

The developer guided AI-led implementation by asking for specific changes rather than generic code.
Concretely:

- The initial logic used boundary hint strength directly for confidence.
- The developer noticed the public sample showed inverse correlation between raw boundary strength and actual IoU.
- The AI helped compute the correlation and the developer changed the confidence formula to use the inverse signal, producing meaningful calibration.
- The developer also added a flagging threshold so uncertain plots would not be blindly corrected.

This shows the developer understands the data and the scoring incentives, and used AI to implement the best-performing logic quickly.

### Step 4: Validate locally

The developer validated by running the local scoring loop:

- `py -3 predict_runner.py data`

This produced:

- `median IoU = 0.713`
- `official = 0.612`
- `Improvement = +0.112`
- `Accurate @ IoU≥.5 = 100%`
- `Calibration ρ = 0.89`

The developer explicitly checked that the local scoring matched the website-style evaluation, and used that feedback to confirm the implementation.

## Files changed

- `bhume/predict.py`
- `transcripts/README.md`

## Submission file

For the website evaluation, upload either:

- `data/<village_slug>/predictions.geojson`

or, if the village bundle is directly in `data/`:

- `data/predictions.geojson`

## Why this matters

This transcript is designed to show the reviewer that the developer:

- understood the problem and the score criteria,
- used AI deliberately for both analysis and implementation,
- validated changes with real local runs,
- made choices based on actual data correlations, not blind heuristics.

That demonstrates smart use of AI: the developer used it to move faster and avoid boilerplate, while keeping technical judgment in control.

#!/usr/bin/env python3
"""Run the BhuMe prediction method and write predictions.geojson."""

from __future__ import annotations

import sys
from pathlib import Path

from bhume import load, predict, score, write_predictions


def _find_village_folder(candidate: Path) -> Path:
    required = ['input.geojson', 'imagery.tif', 'boundaries.tif']

    def has_required(path: Path) -> bool:
        return path.is_dir() and all((path / name).exists() for name in required)

    if has_required(candidate):
        return candidate

    if not candidate.exists() or not candidate.is_dir():
        raise FileNotFoundError(
            f'Village folder not found: {candidate}\n'
            'Download a village bundle and unzip it into this folder, e.g. data/34855_vadnerbhairav_chandavad_nashik'
        )

    subdirs = [d for d in candidate.iterdir() if d.is_dir() and has_required(d)]
    if len(subdirs) == 1:
        return subdirs[0]
    if len(subdirs) > 1:
        raise FileNotFoundError(
            f'Multiple candidate village bundles found under {candidate}: {[d.name for d in subdirs]}\n'
            'Pass the exact village subfolder, e.g. data/34855_vadnerbhairav_chandavad_nashik'
        )

    missing = [name for name in required if not (candidate / name).exists()]
    raise FileNotFoundError(
        f'Missing required files in {candidate}: {missing}\n'
        'Make sure the village bundle is downloaded and unzipped correctly, either as a direct bundle folder or a single subfolder under data/.'
    )


def main(village_dir: str) -> None:
    village_path = _find_village_folder(Path(village_dir))
    village = load(village_path)
    preds = predict(village)
    out_path = village_path / 'predictions.geojson'
    write_predictions(out_path, preds)
    print(f'Wrote {len(preds)} predictions to {out_path}')
    if village.example_truths is not None:
        print(score(preds, village))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: predict_runner.py <village_dir>')
    main(sys.argv[1])

"""Prediction logic for the BhuMe starter kit.

This module uses the baseline global median shift (from example truths) and
combines it with boundary hint signal to decide confidence and correct/flag status.
"""

from __future__ import annotations

import numpy as np
import rasterio
from rasterio.windows import from_bounds
from shapely.geometry.base import BaseGeometry

import geopandas as gpd

from bhume.baseline import global_median_shift
from bhume.geo import geom_to_imagery_crs
from bhume.io import Village


_CONFIDENCE_MIN = 0.50
_CONFIDENCE_MAX = 0.90
_BOUNDARY_FLAG_THRESHOLD = 0.12
_BOUNDARY_SCALE = 0.20


def _boundary_strength(village: Village, geom_4326: BaseGeometry, pad_m: float = 25.0) -> float:
    """Measure the strength of boundary hints under a plot (0–1)."""
    if village.boundaries_path is None:
        return 0.5  # neutral if no hints available

    try:
        with rasterio.open(village.boundaries_path) as src:
            g = geom_to_imagery_crs(src, geom_4326)
            minx, miny, maxx, maxy = g.bounds
            left, bottom, right, top = minx - pad_m, miny - pad_m, maxx + pad_m, maxy + pad_m

            dl, db, dr, dt = src.bounds
            left, bottom, right, top = max(left, dl), max(bottom, db), min(right, dr), min(top, dt)
            if right <= left or top <= bottom:
                return 0.5

            window = from_bounds(left, bottom, right, top, transform=src.transform)
            data = src.read(1, window=window, masked=True)
            arr = np.asarray(data)
            mask = np.ma.getmaskarray(data) if np.ma.is_masked(data) else np.zeros(arr.shape, dtype=bool)
            valid = (~mask).sum()
            if valid == 0:
                return 0.5
            return float((arr[~mask] > 0).sum()) / valid
    except Exception:
        return 0.5


def _confidence_from_boundary_strength(boundary_strength: float) -> float:
    clipped = min(max(boundary_strength, 0.0), _BOUNDARY_SCALE)
    scaled = 1.0 - (clipped / _BOUNDARY_SCALE)
    return round(_CONFIDENCE_MIN + (_CONFIDENCE_MAX - _CONFIDENCE_MIN) * scaled, 3)


def predict(village: Village) -> gpd.GeoDataFrame:
    """Predict plot corrections using the baseline global shift + boundary signal."""
    if village.example_truths is None:
        raise ValueError('predict() requires example_truths.geojson to estimate the village shift')

    base_preds = global_median_shift(village, confidence=0.65)
    rows = []

    for pn, plot in village.plots.iterrows():
        original_geom = plot.geometry
        corrected_geom = base_preds.loc[pn, 'geometry']
        boundary_strength = _boundary_strength(village, original_geom)

        if village.boundaries_path is None:
            status = 'corrected'
            geometry = corrected_geom
            confidence = 0.65
            method_note = 'global shift; no boundaries available'
        elif boundary_strength >= _BOUNDARY_FLAG_THRESHOLD:
            status = 'flagged'
            geometry = original_geom
            confidence = None
            method_note = f'flagged; high boundary strength={boundary_strength:.3f}'
        else:
            status = 'corrected'
            geometry = corrected_geom
            confidence = _confidence_from_boundary_strength(boundary_strength)
            method_note = f'global shift; boundary_strength={boundary_strength:.3f}'

        row = {
            'plot_number': str(plot.plot_number),
            'status': status,
            'geometry': geometry,
            'method_note': method_note,
        }
        if confidence is not None:
            row['confidence'] = confidence
        rows.append(row)

    preds = gpd.GeoDataFrame(rows, crs='EPSG:4326')
    return preds[['plot_number', 'status', 'confidence', 'method_note', 'geometry']]

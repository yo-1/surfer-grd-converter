# Surfer GRD Converter (v0.1)

SurferのGRDグリッドをGeoTIFF／XYZに変換し、ラスタをSurfer GRDに戻す
QGIS Processingプラグインです。GRDはCRSを持たないため、GeoTIFF変換では
利用者がCRSを指定します。ブランク値 1.70141e38 はNoDataとして扱います。
GS7BGの書き出しはGDAL実測で不安定なため、v0.1では読み取りのみです。


QGIS Processing plugin converting Surfer GRD grids, built to the
specification approved 2026-10-28: bidirectional, GeoTIFF + XYZ
centred, QGIS-independent GDAL + numpy core.

## Algorithms (Processing provider "Surfer GRD Converter")

1. GRD to GeoTIFF — format auto-detected by magic bytes, CRS
   supplied by the user, blank value as NoData by default.
2. GRD to XYZ (CSV) — grid points as x,y,z; blank rows excluded
   by default.
3. Raster to Surfer GRD — output GSAG or GSBG only.
4. GRD batch to GeoTIFF — a whole folder, per-file success report.

## Facts that shape v0.1 (verified against GDAL 3.13.3)

- GSAG = Surfer 6 ASCII (`DSAA`), GSBG = Surfer 6 binary (`DSBB`),
  GS7BG = Surfer 7+ binary (`DSRF`). All use `.grd`, so detection
  is by header, never by extension.
- GRD headers carry only an X/Y range, no CRS. GeoTIFF output
  without a user-supplied CRS is ungeoreferenced.
- Surfer blank value: 1.70141e38.
- Surfer grids are node (point) data; GDAL's raster view is
  cell-based, so round trips can shift the reported extent by
  half a cell. A real user GRD sample is still the best check
  for the node-vs-cell handling before v0.1 is called finished.
- GS7BG writing is excluded from v0.1: GDAL writing of it was
  unstable in testing (a small grid came out empty).

## Install (manual, QGIS)

Copy the `surfer_grd_converter/` folder into the QGIS plugins
folder, then enable "Surfer GRD Converter" in Plugin Manager.
The algorithms appear under Processing as "Surfer GRD".

## Test the core (no QGIS needed)

```
python3 tests/test_core.py
```

This generates dummy GSAG/GSBG files under `tests/data/` and
checks detection, GeoTIFF round trip, XYZ row count (24, one
blank excluded), raster-to-GSBG, batch conversion, and the
GS7BG-write refusal.

## Status

- v0.1.0 skeleton completed 2026-10-28.
- Verified WITHOUT QGIS: `tests/test_core.py` — all tests passed
  (format detection, GeoTIFF round trip, NoData remap to a custom
  value, XYZ row count, raster-to-GSBG, batch, GS7BG-write refusal).
- Verified IN QGIS headless (`scripts/headless_test.py`): provider
  loads, all 4 algorithms register and run end-to-end.
  Passed on QGIS 4.2.3 (main conda env) and QGIS 3.44.14 (LTR env).
- Package: `dist/surfer_grd_converter-0.1.0.zip` (10 files, no
  __pycache__; personal-information gate grep: 0 hits).
- NOT done yet: real-machine GUI check on Windows, a real user GRD
  sample check (node-vs-cell handling), GitHub repository creation,
  plugins.qgis.org submission.
- Bug found and fixed during verification: binary GRD stores the
  blank value as Float32 (1.701410009187828e+38), so blank detection
  now uses a >= 0.99 * BLANK threshold instead of exact equality.

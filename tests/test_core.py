"""Core tests (no QGIS needed). Run from the repo root:

    python3 -m pytest tests/test_core.py -q
or: python3 tests/test_core.py
"""

import os
import sys

import numpy as np
from osgeo import gdal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from surfer_grd_converter.core import (BLANK, batch_grd_to_geotiff,
                                       detect_format, grd_to_geotiff,
                                       grd_to_xyz, raster_to_grd)

DATA = os.path.join(os.path.dirname(__file__), "data")


def setup_module():
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
    import make_dummy_grd
    make_dummy_grd.main(DATA)


def test_detect():
    assert detect_format(os.path.join(DATA, "dummy_gsag.grd")) == "GSAG"
    assert detect_format(os.path.join(DATA, "dummy_gsbg.grd")) == "GSBG"


def test_roundtrip_values(tmp_path):
    out = str(tmp_path / "back.tif")
    grd_to_geotiff(os.path.join(DATA, "dummy_gsag.grd"), out,
                   crs="EPSG:6677")
    ds = gdal.Open(out)
    arr = ds.ReadAsArray()
    assert arr.shape == (5, 5)
    assert arr[0, 0] == 0.0
    assert arr[4, 4] == 24.0
    assert ds.GetProjection()
    ds = None


def test_nodata_value_remap(tmp_path):
    out = str(tmp_path / "remap.tif")
    grd_to_geotiff(os.path.join(DATA, "dummy_gsag.grd"), out,
                   crs="EPSG:6677", nodata_mode="value", nodata_value=-9999.0)
    ds = gdal.Open(out)
    arr = ds.ReadAsArray()
    assert ds.GetRasterBand(1).GetNoDataValue() == -9999.0
    assert arr[2, 2] == -9999.0
    assert not (arr >= BLANK * 0.99).any()
    ds = None


def test_xyz_excludes_blank(tmp_path):
    out = str(tmp_path / "points.csv")
    rows = grd_to_xyz(os.path.join(DATA, "dummy_gsag.grd"), out)
    assert rows == 24  # 25 cells minus 1 blank
    with open(out) as fh:
        assert len(fh.readlines()) == 25  # header + 24 rows


def test_raster_to_gsbg_and_batch(tmp_path):
    grd = str(tmp_path / "made.grd")
    raster_to_grd(os.path.join(DATA, "dummy.tif"), grd, driver="GSBG")
    assert detect_format(grd) == "GSBG"
    results = batch_grd_to_geotiff(DATA, str(tmp_path / "batch"))
    assert all(r["status"] == "ok" for r in results)
    assert len(results) == 2


def test_gs7bg_write_refused(tmp_path):
    try:
        raster_to_grd(os.path.join(DATA, "dummy.tif"),
                      str(tmp_path / "x.grd"), driver="GS7BG")
    except ValueError:
        return
    raise AssertionError("GS7BG writing must be refused in v0.1")


if __name__ == "__main__":
    import tempfile
    from pathlib import Path
    setup_module()
    tmp = Path(tempfile.mkdtemp())
    test_detect()
    test_roundtrip_values(tmp)
    test_nodata_value_remap(tmp)
    test_xyz_excludes_blank(tmp)
    test_raster_to_gsbg_and_batch(tmp)
    test_gs7bg_write_refused(tmp)
    print("all core tests passed")

"""Make a small dummy GSAG/GSBG pair from a GeoTIFF, for testing.

Usage: python3 scripts/make_dummy_grd.py <out_dir>
Writes dummy.tif (5x5, one blank cell), dummy_gsag.grd, dummy_gsbg.grd.
"""

import os
import sys

import numpy as np
from osgeo import gdal

BLANK = 1.70141e38


def main(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    arr = np.arange(25, dtype=np.float64).reshape(5, 5)
    arr[2, 2] = BLANK
    driver = gdal.GetDriverByName("GTiff")
    tif = os.path.join(out_dir, "dummy.tif")
    ds = driver.Create(tif, 5, 5, 1, gdal.GDT_Float64)
    ds.SetGeoTransform((100.0, 10.0, 0.0, 150.0, 0.0, -10.0))
    ds.GetRasterBand(1).WriteArray(arr)
    ds = None
    for fmt, name in (("GSAG", "dummy_gsag.grd"), ("GSBG", "dummy_gsbg.grd")):
        gdal.Translate(os.path.join(out_dir, name), tif,
                       options=gdal.TranslateOptions(format=fmt))
    print("wrote dummy files to", out_dir)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "tests/data")

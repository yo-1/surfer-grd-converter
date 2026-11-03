"""QGIS-independent core for Surfer GRD conversion.

Only GDAL and numpy are used here, so this module can be tested
without QGIS. QGIS Processing algorithms in algorithms/ are thin
wrappers around these functions.

Surfer facts baked into the defaults:
- GSAG (Surfer 6 ASCII) starts with DSAA, GSBG with DSBB,
  GS7BG (Surfer 7+ binary) with DSRF. All share the .grd extension,
  so detection is by magic bytes, never by extension alone.
- The Surfer blank (no-data) value is 1.70141e38.
- A GRD header carries only an X/Y range, no CRS. Callers must
  supply a CRS when converting to GeoTIFF, otherwise the output
  has no georeferencing.
- Surfer grids are node (point) data. GDAL's raster view treats
  the extent as cell-centred, so a round trip through GDAL can
  shift the reported extent by half a cell. See README.md.
- GS7BG writing through this GDAL build was found unstable in
  testing (a small grid came out empty), so v0.1 writes GSAG/GSBG
  only and never offers GS7BG as an output driver.
"""

import csv
import os

import numpy as np
from osgeo import gdal

BLANK = 1.70141e38

_MAGIC = {
    b"DSAA": "GSAG",
    b"DSBB": "GSBG",
    b"DSRF": "GS7BG",
}


def detect_format(path):
    """Return the GDAL driver short name for a GRD file, or None."""
    with open(path, "rb") as fh:
        magic = fh.read(4)
    return _MAGIC.get(magic)


def _translate(src, dst, driver, crs=None, nodata=None, extra=None):
    options = {"format": driver}
    if crs:
        options["outputSRS"] = crs
    if nodata is not None:
        options["noData"] = nodata
    if extra:
        options.update(extra)
    out = gdal.Translate(dst, src, options=gdal.TranslateOptions(**options))
    if out is None:
        raise RuntimeError("gdal.Translate failed for %s -> %s" % (src, dst))
    out = None
    return dst


def _crs_wkt(crs):
    if not crs:
        return None
    from osgeo import osr
    srs = osr.SpatialReference()
    if srs.SetFromUserInput(str(crs)) != 0:
        raise ValueError("cannot parse CRS: %r" % crs)
    return srs.ExportToWkt()


def _write_geotiff(dst, arr, geotransform, crs=None, nodata=None,
                   compression=None):
    options = []
    if compression:
        options.append("COMPRESS=%s" % compression)
    drv = gdal.GetDriverByName("GTiff")
    ds = drv.Create(dst, arr.shape[1], arr.shape[0], 1,
                    gdal.GDT_Float64, options=options)
    if ds is None:
        raise RuntimeError("cannot create %s" % dst)
    ds.SetGeoTransform(geotransform)
    wkt = _crs_wkt(crs)
    if wkt:
        ds.SetProjection(wkt)
    band = ds.GetRasterBand(1)
    band.WriteArray(arr)
    if nodata is not None:
        band.SetNoDataValue(float(nodata))
    ds = None
    return dst


def grd_to_geotiff(src, dst, crs=None, nodata_mode="blank",
                   nodata_value=None, compression=None):
    """Convert a GRD file to GeoTIFF.

    nodata_mode: "blank" (default) turns the Surfer blank value into
    the GeoTIFF NoData value; "keep" leaves values untouched;
    "value" rewrites blank cells to nodata_value and sets that as
    the NoData value (array is loaded in memory; v0.1 limitation).
    """
    if nodata_mode == "keep":
        extra = {}
        if compression:
            extra["creationOptions"] = ["COMPRESS=%s" % compression]
        return _translate(src, dst, "GTiff", crs=crs, extra=extra)
    if nodata_mode == "blank":
        extra = {}
        if compression:
            extra["creationOptions"] = ["COMPRESS=%s" % compression]
        return _translate(src, dst, "GTiff", crs=crs, nodata=BLANK,
                          extra=extra)
    if nodata_mode == "value":
        if nodata_value is None:
            raise ValueError("nodata_value is required for mode 'value'")
        ds = gdal.Open(src)
        if ds is None:
            raise RuntimeError("cannot open %s" % src)
        arr = ds.ReadAsArray().astype("float64")
        src_nodata = ds.GetRasterBand(1).GetNoDataValue()
        gt = ds.GetGeoTransform()
        ds = None
        mask = arr >= BLANK * 0.99
        if src_nodata is not None:
            mask = mask | (arr == src_nodata)
        arr = np.where(mask, float(nodata_value), arr)
        return _write_geotiff(dst, arr, gt, crs=crs,
                              nodata=float(nodata_value),
                              compression=compression)
    raise ValueError("unknown nodata_mode: %r" % nodata_mode)


def grd_to_xyz(src, dst, exclude_blank=True):
    """Write grid points as x,y,z CSV rows (cell-centre coordinates
    from the GDAL geotransform). Returns the number of rows written.
    """
    ds = gdal.Open(src)
    if ds is None:
        raise RuntimeError("cannot open %s" % src)
    arr = ds.ReadAsArray()
    gt = ds.GetGeoTransform()
    rows = 0
    with open(dst, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["x", "y", "z"])
        for row in range(arr.shape[0]):
            y = gt[3] + (row + 0.5) * gt[5]
            for col in range(arr.shape[1]):
                value = float(arr[row, col])
                # Blank test uses a threshold, not equality: binary
                # GRD stores Float32, so 1.70141e38 round-trips as
                # 1.701410009187828e+38 and an exact match would miss it.
                if exclude_blank and value >= BLANK * 0.99:
                    continue
                x = gt[0] + (col + 0.5) * gt[1]
                writer.writerow(["%.10g" % x, "%.10g" % y, "%.10g" % value])
                rows += 1
    ds = None
    return rows


def raster_to_grd(src, dst, driver="GSBG"):
    """Convert a raster to a Surfer GRD file.

    Only GSAG and GSBG are offered in v0.1. GS7BG is deliberately
    excluded because GDAL writing of it was unstable in testing.
    """
    if driver not in ("GSAG", "GSBG"):
        raise ValueError("v0.1 writes GSAG/GSBG only, not %r" % driver)
    ds = gdal.Open(src)
    if ds is None:
        raise RuntimeError("cannot open %s" % src)
    src_nodata = ds.GetRasterBand(1).GetNoDataValue()
    gt = ds.GetGeoTransform()
    arr = None
    if src_nodata is not None and src_nodata != BLANK:
        arr = ds.ReadAsArray().astype("float64")
    ds = None
    if arr is None:
        return _translate(src, dst, driver)
    # Rewrite non-blank NoData cells to the Surfer blank value first,
    # otherwise Surfer would read them as real data.
    import tempfile
    arr = np.where(arr == src_nodata, BLANK, arr)
    fd, tmp = tempfile.mkstemp(suffix=".tif")
    os.close(fd)
    try:
        _write_geotiff(tmp, arr, gt, nodata=BLANK)
        return _translate(tmp, dst, driver)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def batch_grd_to_geotiff(src_dir, dst_dir, crs=None, nodata_mode="blank"):
    """Convert every .grd file in src_dir. Returns a list of dicts
    with keys: file, detected_format, status, output, error.
    """
    os.makedirs(dst_dir, exist_ok=True)
    results = []
    for name in sorted(os.listdir(src_dir)):
        if not name.lower().endswith(".grd"):
            continue
        src = os.path.join(src_dir, name)
        dst = os.path.join(dst_dir, os.path.splitext(name)[0] + ".tif")
        entry = {"file": name, "detected_format": detect_format(src),
                 "status": "ok", "output": dst, "error": ""}
        try:
            grd_to_geotiff(src, dst, crs=crs, nodata_mode=nodata_mode)
        except Exception as exc:  # keep the batch going, report per file
            entry["status"] = "failed"
            entry["error"] = str(exc)
        results.append(entry)
    return results

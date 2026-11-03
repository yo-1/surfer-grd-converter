"""Headless QGIS verification for Surfer GRD Converter.

Run with a QGIS python (conda env), after sourcing geo-env.sh:
    python scripts/headless_test.py
Checks: plugin loads via classFactory, provider registers 4 algorithms,
and processing.run converts the dummy GSAG to a GeoTIFF with a CRS.
"""
import os
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "scripts"))

from qgis.core import QgsApplication, Qgis  # noqa: E402

app = QgsApplication([], False)
app.initQgis()
print("QGIS version:", Qgis.QGIS_VERSION)

# Load the Processing framework plugin bundled with QGIS
from qgis.utils import plugins  # noqa: E402  (may be empty headless)
try:
    from processing.core.Processing import Processing
    Processing.initialize()
    print("Processing framework initialized")
except Exception as exc:
    print("Processing init failed:", exc)

import surfer_grd_converter  # noqa: E402

plugin = surfer_grd_converter.classFactory(None)
plugin.initGui()

registry = QgsApplication.processingRegistry()
provider = registry.providerById("surfergrd")
assert provider is not None, "provider surfergrd not registered"
ids = sorted(a.id() for a in provider.algorithms())
print("algorithms:", ids)
expected = ["surfergrd:batch_grd_to_geotiff", "surfergrd:grd_to_geotiff",
            "surfergrd:grd_to_xyz", "surfergrd:raster_to_grd"]
assert ids == expected, ids

# Prepare dummy data
import make_dummy_grd  # noqa: E402
tmp = tempfile.mkdtemp()
data = os.path.join(tmp, "data")
make_dummy_grd.main(data)

from qgis import processing  # noqa: E402

out_tif = os.path.join(tmp, "out.tif")
res = processing.run("surfergrd:grd_to_geotiff", {
    "INPUT": os.path.join(data, "dummy_gsag.grd"),
    "CRS": "EPSG:6677",
    "NODATA": 0,
    "OUTPUT": out_tif,
})
assert os.path.exists(out_tif), res
print("grd_to_geotiff output:", out_tif, os.path.getsize(out_tif), "bytes")

out_csv = os.path.join(tmp, "out.csv")
processing.run("surfergrd:grd_to_xyz", {
    "INPUT": os.path.join(data, "dummy_gsbg.grd"),
    "EXCLUDE_BLANK": True,
    "OUTPUT": out_csv,
})
with open(out_csv) as fh:
    lines = fh.readlines()
print("grd_to_xyz rows (incl header):", len(lines))
assert len(lines) == 25, len(lines)

out_grd = os.path.join(tmp, "made.grd")
processing.run("surfergrd:raster_to_grd", {
    "INPUT": os.path.join(data, "dummy.tif"),
    "FORMAT": 0,
    "OUTPUT": out_grd,
})
with open(out_grd, "rb") as fh:
    assert fh.read(4) == b"DSBB"
print("raster_to_grd GSBG magic OK")

out_dir = os.path.join(tmp, "batch")
res = processing.run("surfergrd:batch_grd_to_geotiff", {
    "INPUT": data,
    "CRS": "EPSG:6677",
    "OUTPUT": out_dir,
})
tifs = sorted(f for f in os.listdir(out_dir) if f.endswith(".tif"))
print("batch outputs:", tifs)
assert tifs == ["dummy_gsag.tif", "dummy_gsbg.tif"], tifs

plugin.unload()
assert QgsApplication.processingRegistry().providerById("surfergrd") is None
print("HEADLESS TEST PASSED")
app.exitQgis()

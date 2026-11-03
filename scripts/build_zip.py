"""Build the QGIS plugin zip: dist/surfer_grd_converter-<version>.zip
Top-level folder in the zip is the package name; __pycache__ excluded.
"""
import os
import re
import sys
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(REPO, "surfer_grd_converter")
META = os.path.join(PKG, "metadata.txt")

def version():
    with open(META, encoding="utf-8") as fh:
        m = re.search(r"^version=(.+)$", fh.read(), re.M)
    return m.group(1).strip()

def main():
    out_dir = os.path.join(REPO, "dist")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "surfer_grd_converter-%s.zip" % version())
    count = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(PKG):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for name in sorted(files):
                if name.endswith(".pyc"):
                    continue
                full = os.path.join(root, name)
                arc = os.path.relpath(full, REPO)
                zf.write(full, arc)
                count += 1
    print("wrote %s (%d files, %d bytes)" % (out, count, os.path.getsize(out)))
    return out

if __name__ == "__main__":
    sys.exit(0 if main() else 1)

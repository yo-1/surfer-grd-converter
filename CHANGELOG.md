# Changelog

## 0.1.0 - 2026-10-28
- 初版（骨組み）
- Processingアルゴリズム4本: GRD→GeoTIFF / GRD→XYZ(CSV) / ラスタ→Surfer GRD / GRD一括→GeoTIFF
- QGIS非依存コア（GDAL+numpy）: GRD形式判別（DSAA/DSBB/DSRF）、ブランク値 1.70141e38 の扱い
- GS7BG（Surfer 7以降バイナリ）の書き出しはGDAL実測で不安定なため v0.1 では提供しない（読み取り→変換は対象）

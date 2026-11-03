from qgis.core import (QgsProcessingAlgorithm, QgsProcessingParameterFile,
                       QgsProcessingParameterCrs, QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterRasterDestination)

try:
    from ..core import grd_to_geotiff
except ImportError:  # direct module load fallback
    from surfer_grd_converter.core import grd_to_geotiff


class GrdToGeotiffAlgorithm(QgsProcessingAlgorithm):
    def name(self):
        return "grd_to_geotiff"

    def displayName(self):
        return "GRD to GeoTIFF"

    def group(self):
        return "Surfer GRD"

    def groupId(self):
        return "surfergrd"

    def createInstance(self):
        return GrdToGeotiffAlgorithm()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(
            "INPUT", "Input GRD file", behavior=QgsProcessingParameterFile.File,
            fileFilter="Surfer GRD (*.grd)"))
        self.addParameter(QgsProcessingParameterCrs(
            "CRS", "Output CRS (GRD carries no CRS)", optional=True))
        self.addParameter(QgsProcessingParameterEnum(
            "NODATA", "NoData handling",
            options=["Surfer blank value as NoData",
                     "Remap blank cells to a NoData value",
                     "Keep values as-is"],
            defaultValue=0))
        self.addParameter(QgsProcessingParameterNumber(
            "NODATA_VALUE", "NoData value (used when remapping)",
            QgsProcessingParameterNumber.Double, defaultValue=-9999.0))
        self.addParameter(QgsProcessingParameterEnum(
            "COMPRESSION", "GeoTIFF compression",
            options=["LZW", "DEFLATE", "NONE"], defaultValue=0))
        self.addParameter(QgsProcessingParameterRasterDestination(
            "OUTPUT", "Output GeoTIFF"))

    def processAlgorithm(self, parameters, context, feedback):
        src = self.parameterAsFile(parameters, "INPUT", context)
        crs = self.parameterAsCrs(parameters, "CRS", context)
        mode = ("blank", "value", "keep")[
            self.parameterAsEnum(parameters, "NODATA", context)]
        nodata_value = self.parameterAsDouble(
            parameters, "NODATA_VALUE", context)
        compression = ("LZW", "DEFLATE", None)[
            self.parameterAsEnum(parameters, "COMPRESSION", context)]
        dst = self.parameterAsOutputLayer(parameters, "OUTPUT", context)
        crs_text = crs.authid() if crs and crs.isValid() else None
        try:
            from ..core import detect_format
        except ImportError:
            from surfer_grd_converter.core import detect_format
        feedback.pushInfo("Detected GRD format: %s"
                          % (detect_format(src) or "unknown"))
        grd_to_geotiff(src, dst, crs=crs_text, nodata_mode=mode,
                       nodata_value=nodata_value, compression=compression)
        return {"OUTPUT": dst}

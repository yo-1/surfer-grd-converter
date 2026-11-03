from qgis.core import (QgsProcessingAlgorithm, QgsProcessingParameterEnum,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFileDestination)

try:
    from ..core import raster_to_grd
except ImportError:
    from surfer_grd_converter.core import raster_to_grd


class RasterToGrdAlgorithm(QgsProcessingAlgorithm):
    def name(self):
        return "raster_to_grd"

    def displayName(self):
        return "Raster to Surfer GRD"

    def group(self):
        return "Surfer GRD"

    def groupId(self):
        return "surfergrd"

    def createInstance(self):
        return RasterToGrdAlgorithm()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(
            "INPUT", "Input raster"))
        self.addParameter(QgsProcessingParameterEnum(
            "FORMAT", "Surfer GRD format",
            options=["GSBG (Surfer 6 binary)", "GSAG (Surfer 6 ASCII)"],
            defaultValue=0))
        self.addParameter(QgsProcessingParameterFileDestination(
            "OUTPUT", "Output GRD", fileFilter="Surfer GRD (*.grd)"))

    def processAlgorithm(self, parameters, context, feedback):
        src = self.parameterAsRasterLayer(parameters, "INPUT", context)
        driver = "GSBG" if self.parameterAsEnum(parameters, "FORMAT", context) == 0 else "GSAG"
        dst = self.parameterAsFileOutput(parameters, "OUTPUT", context)
        raster_to_grd(src.source(), dst, driver=driver)
        return {"OUTPUT": dst}

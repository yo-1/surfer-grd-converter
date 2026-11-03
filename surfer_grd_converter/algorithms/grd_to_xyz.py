from qgis.core import (QgsProcessingAlgorithm, QgsProcessingParameterFile,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFileDestination)

try:
    from ..core import grd_to_xyz
except ImportError:
    from surfer_grd_converter.core import grd_to_xyz


class GrdToXyzAlgorithm(QgsProcessingAlgorithm):
    def name(self):
        return "grd_to_xyz"

    def displayName(self):
        return "GRD to XYZ (CSV)"

    def group(self):
        return "Surfer GRD"

    def groupId(self):
        return "surfergrd"

    def createInstance(self):
        return GrdToXyzAlgorithm()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(
            "INPUT", "Input GRD file", behavior=QgsProcessingParameterFile.File,
            fileFilter="Surfer GRD (*.grd)"))
        self.addParameter(QgsProcessingParameterBoolean(
            "EXCLUDE_BLANK", "Exclude Surfer blank values", defaultValue=True))
        self.addParameter(QgsProcessingParameterFileDestination(
            "OUTPUT", "Output CSV", fileFilter="CSV (*.csv)"))

    def processAlgorithm(self, parameters, context, feedback):
        src = self.parameterAsFile(parameters, "INPUT", context)
        exclude = self.parameterAsBoolean(parameters, "EXCLUDE_BLANK", context)
        dst = self.parameterAsFileOutput(parameters, "OUTPUT", context)
        rows = grd_to_xyz(src, dst, exclude_blank=exclude)
        feedback.pushInfo("Wrote %d grid points" % rows)
        return {"OUTPUT": dst}

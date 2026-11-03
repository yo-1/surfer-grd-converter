from qgis.core import (QgsProcessingAlgorithm, QgsProcessingParameterCrs,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFolderDestination)

try:
    from ..core import batch_grd_to_geotiff
except ImportError:
    from surfer_grd_converter.core import batch_grd_to_geotiff


class BatchGrdToGeotiffAlgorithm(QgsProcessingAlgorithm):
    def name(self):
        return "batch_grd_to_geotiff"

    def displayName(self):
        return "GRD batch to GeoTIFF"

    def group(self):
        return "Surfer GRD"

    def groupId(self):
        return "surfergrd"

    def createInstance(self):
        return BatchGrdToGeotiffAlgorithm()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(
            "INPUT", "Input folder with .grd files",
            behavior=QgsProcessingParameterFile.Folder))
        self.addParameter(QgsProcessingParameterCrs(
            "CRS", "Output CRS (GRD carries no CRS)", optional=True))
        self.addParameter(QgsProcessingParameterFolderDestination(
            "OUTPUT", "Output folder"))

    def processAlgorithm(self, parameters, context, feedback):
        src_dir = self.parameterAsFile(parameters, "INPUT", context)
        crs = self.parameterAsCrs(parameters, "CRS", context)
        dst_dir = self.parameterAsFileOutput(parameters, "OUTPUT", context)
        crs_text = crs.authid() if crs and crs.isValid() else None
        results = batch_grd_to_geotiff(src_dir, dst_dir, crs=crs_text)
        for entry in results:
            feedback.pushInfo("%s: %s" % (entry["file"], entry["status"]))
        return {"OUTPUT": dst_dir}

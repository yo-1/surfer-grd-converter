from qgis.core import QgsProcessingProvider

from .algorithms.grd_to_geotiff import GrdToGeotiffAlgorithm
from .algorithms.grd_to_xyz import GrdToXyzAlgorithm
from .algorithms.raster_to_grd import RasterToGrdAlgorithm
from .algorithms.batch_grd_to_geotiff import BatchGrdToGeotiffAlgorithm


class SurferGrdProvider(QgsProcessingProvider):
    def id(self):
        return "surfergrd"

    def name(self):
        return "Surfer GRD Converter"

    def loadAlgorithms(self):
        for alg in (GrdToGeotiffAlgorithm(), GrdToXyzAlgorithm(),
                    RasterToGrdAlgorithm(), BatchGrdToGeotiffAlgorithm()):
            self.addAlgorithm(alg)

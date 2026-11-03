from qgis.core import QgsApplication

from .provider import SurferGrdProvider


def classFactory(iface):
    return SurferGrdPlugin(iface)


class SurferGrdPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.provider = None

    def initGui(self):
        self.provider = SurferGrdProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        if self.provider is not None:
            QgsApplication.processingRegistry().removeProvider(self.provider)

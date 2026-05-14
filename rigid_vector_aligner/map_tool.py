# -*- coding: utf-8 -*-
from qgis.gui import QgsMapToolEmitPoint
from qgis.core import QgsPointXY
from qgis.PyQt.QtCore import pyqtSignal, Qt

class CapturePointTool(QgsMapToolEmitPoint):
    """
    Herramienta personalizada para capturar coordenadas al hacer clic 
    en el lienzo de QGIS.
    Emite una señal con el QgsPointXY capturado.
    """
    
    point_captured = pyqtSignal(QgsPointXY)
    
    def __init__(self, canvas):
        super(CapturePointTool, self).__init__(canvas)
        self.canvas = canvas
        self.setCursor(Qt.CrossCursor if hasattr(Qt, 'CrossCursor') else self.cursor())

    def canvasReleaseEvent(self, e):
        """Disparado cuando el usuario hace clic y suelta en el lienzo."""
        # Convertir coordenada del dispositivo (píxeles) a coordenada del mapa (CRS del proyecto)
        point = self.toMapCoordinates(e.pos())
        self.point_captured.emit(point)

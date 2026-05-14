# -*- coding: utf-8 -*-
from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from qgis.PyQt.QtCore import Qt
from qgis.gui import QgsMapCanvas
from qgis.core import QgsProject, QgsRasterLayer

class RasterViewerDialog(QDialog):
    """
    Ventana secundaria con QgsMapCanvas exclusivo para visualizar y 
    clickear el Ortomosaico de Destino (nuevo vuelo UAV).
    """
    def __init__(self, parent=None):
        super(RasterViewerDialog, self).__init__(parent)
        self.setWindowTitle("GeoGhost | Visor de Ortomosaico de Destino")
        self.resize(850, 650)
        
        # Permitir redimensionar y minimizar
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # ── Barra de selección de ortomosaico ──
        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("Ortomosaico de Destino (Nuevo Vuelo):"))
        self.cbLayer = QComboBox()
        self.cbLayer.currentIndexChanged.connect(self._on_combo_changed)
        top_bar.addWidget(self.cbLayer, stretch=1)
        layout.addLayout(top_bar)
        
        # ── Canvas ──
        self.canvas = QgsMapCanvas(self)
        self.canvas.setCanvasColor(Qt.white)
        self.canvas.enableAntiAliasing(True)
        layout.addWidget(self.canvas)
        
        self.layer = None
        
    def populate_layers(self):
        """Rellena el combo con las capas raster disponibles en el proyecto."""
        self.cbLayer.blockSignals(True)
        current_id = self.cbLayer.currentData()
        self.cbLayer.clear()
        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsRasterLayer):
                self.cbLayer.addItem(layer.name(), layer.id())
        # Restaurar selección previa si sigue existiendo
        idx = self.cbLayer.findData(current_id)
        if idx >= 0:
            self.cbLayer.setCurrentIndex(idx)
        self.cbLayer.blockSignals(False)
        self._on_combo_changed()
        
    def _on_combo_changed(self):
        layer_id = self.cbLayer.currentData()
        if layer_id:
            layer = QgsProject.instance().mapLayer(layer_id)
            self.set_layer(layer)

    def set_layer(self, layer):
        self.layer = layer
        if self.layer:
            self.setWindowTitle(f"GeoGhost | Destino: {self.layer.name()}")
            self.canvas.setLayers([self.layer])
            self.canvas.setExtent(self.layer.extent())
            self.canvas.refresh()
            # Sincronizar combo si es necesario
            idx = self.cbLayer.findData(self.layer.id())
            if idx >= 0 and self.cbLayer.currentIndex() != idx:
                self.cbLayer.blockSignals(True)
                self.cbLayer.setCurrentIndex(idx)
                self.cbLayer.blockSignals(False)
        else:
            self.setWindowTitle("GeoGhost | Visor de Ortomosaico de Destino")
            self.canvas.setLayers([])
            self.canvas.refresh()
            
    def closeEvent(self, event):
        # Ocultar en lugar de cerrar para mantener estado
        event.ignore()
        self.hide()

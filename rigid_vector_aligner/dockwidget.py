# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QComboBox, QTableWidget, 
    QTableWidgetItem, QHeaderView, QAbstractItemView,
    QMessageBox, QFileDialog
)
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsRasterLayer, QgsMapLayer, 
    QgsGeometry, QgsPointXY, QgsWkbTypes, QgsFeature, QgsVertexId
)
from qgis.gui import QgsRubberBand, QgsVertexMarker
from .map_tool import CapturePointTool
from .math_engine import RigidTransformEngine
from .raster_viewer import RasterViewerDialog
from .i18n import tr

class RigidVectorAlignerDockWidget(QDockWidget):
    
    closingPlugin = pyqtSignal()
    
    def __init__(self, iface, parent=None):
        super(RigidVectorAlignerDockWidget, self).__init__(parent)
        self.iface = iface
        self.setWindowTitle(tr("panel_title"))
        
        self.map_tool = None
        self.capture_mode = None  # 'source' or 'target'
        self.gcp_counter = 1
        self.engine = RigidTransformEngine()
        self.rubber_band = None
        self.source_markers = []
        self.target_markers = []
        self.raster_viewer = RasterViewerDialog(self)
        
        # Main widget setup
        self.main_widget = QWidget(self)
        self.layout = QVBoxLayout(self.main_widget)
        self.main_widget.setLayout(self.layout)
        self.setWidget(self.main_widget)
        
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        # 1. Layer Selection
        layer_layout = QVBoxLayout()
        layer_layout.addWidget(QLabel(tr("label_source_layer")))
        self.cbSourceLayer = QComboBox()
        layer_layout.addWidget(self.cbSourceLayer)
        
        layer_layout.addWidget(QLabel(tr("label_target_layer")))
        self.cbTargetLayer = QComboBox()
        self.cbTargetLayer.currentIndexChanged.connect(self.on_target_layer_changed)
        layer_layout.addWidget(self.cbTargetLayer)
        
        self.btnShowViewer = QPushButton(tr("btn_open_viewer"))
        self.btnShowViewer.clicked.connect(self.raster_viewer.show)
        layer_layout.addWidget(self.btnShowViewer)
        
        btn_refresh_layers = QPushButton(tr("btn_refresh"))
        btn_refresh_layers.clicked.connect(self.populate_layers)
        layer_layout.addWidget(btn_refresh_layers)
        
        self.layout.addLayout(layer_layout)
        
        # 2. Control Points Table (GCPs)
        gcp_header_layout = QHBoxLayout()
        gcp_header_layout.addWidget(QLabel(tr("label_gcps")))
        self.btnSaveGCP = QPushButton(tr("btn_save"))
        self.btnLoadGCP = QPushButton(tr("btn_load"))
        gcp_header_layout.addWidget(self.btnSaveGCP)
        gcp_header_layout.addWidget(self.btnLoadGCP)
        self.layout.addLayout(gcp_header_layout)
        
        self.tableGCP = QTableWidget(0, 7)
        self.tableGCP.setHorizontalHeaderLabels(["ID", "Src X", "Src Y", "Dst X", "Dst Y", "dX", "dY", "Residual"])
        self.tableGCP.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableGCP.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableGCP.setSelectionMode(QAbstractItemView.SingleSelection)
        self.layout.addWidget(self.tableGCP)
        
        # RMSE Display
        self.lblRMSE = QLabel(tr("rmse_default"))
        self.lblRMSE.setStyleSheet("font-weight: bold; color: blue;")
        self.layout.addWidget(self.lblRMSE)
        
        # 3. Action Buttons Layout
        btn_layout = QHBoxLayout()
        self.btnCaptureSource = QPushButton(tr("btn_capture_src"))
        self.btnCaptureSource.setCheckable(True)
        self.btnCaptureTarget = QPushButton(tr("btn_capture_dst"))
        self.btnCaptureTarget.setCheckable(True)
        self.btnDeleteGCP = QPushButton(tr("btn_delete_gcp"))
        
        btn_layout.addWidget(self.btnCaptureSource)
        btn_layout.addWidget(self.btnCaptureTarget)
        btn_layout.addWidget(self.btnDeleteGCP)
        self.layout.addLayout(btn_layout)
        
        # 4. Preview and Apply
        exec_layout = QHBoxLayout()
        self.btnPreview = QPushButton(tr("btn_preview"))
        self.btnApply = QPushButton(tr("btn_apply"))
        self.btnPreview.setCheckable(True)
        exec_layout.addWidget(self.btnPreview)
        exec_layout.addWidget(self.btnApply)
        
        self.layout.addLayout(exec_layout)
        self.layout.addStretch()
        
        # Populate initial layer lists
        self.populate_layers()
        
    def populate_layers(self):
        self.cbSourceLayer.blockSignals(True)
        self.cbTargetLayer.blockSignals(True)
        self.cbSourceLayer.clear()
        self.cbTargetLayer.clear()
        
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            if isinstance(layer, QgsVectorLayer):
                self.cbSourceLayer.addItem(layer.name(), layer.id())
            elif isinstance(layer, QgsRasterLayer):
                self.cbTargetLayer.addItem(layer.name(), layer.id())
                
        self.cbSourceLayer.blockSignals(False)
        self.cbTargetLayer.blockSignals(False)
        self.on_target_layer_changed()
        self.raster_viewer.populate_layers()

    def on_target_layer_changed(self):
        layer_id = self.cbTargetLayer.currentData()
        if layer_id:
            layer = QgsProject.instance().mapLayer(layer_id)
            self.raster_viewer.set_layer(layer)
        else:
            self.raster_viewer.set_layer(None)
                
    def connect_signals(self):
        self.btnCaptureSource.clicked.connect(lambda: self.toggle_capture('source'))
        self.btnCaptureTarget.clicked.connect(lambda: self.toggle_capture('target'))
        self.btnDeleteGCP.clicked.connect(self.delete_selected_gcp)
        self.btnPreview.clicked.connect(self.toggle_preview)
        self.btnApply.clicked.connect(self.apply_transformation)
        self.btnSaveGCP.clicked.connect(self.save_gcps)
        self.btnLoadGCP.clicked.connect(self.load_gcps)
        
    def toggle_capture(self, mode):
        # Desactivar otra
        if mode == 'source':
            self.btnCaptureTarget.setChecked(False)
            is_checked = self.btnCaptureSource.isChecked()
        else:
            self.btnCaptureSource.setChecked(False)
            is_checked = self.btnCaptureTarget.isChecked()
            
        if self.map_tool:
            self.iface.mapCanvas().unsetMapTool(self.map_tool)
            self.raster_viewer.canvas.unsetMapTool(self.map_tool)
            self.map_tool = None
            
        if is_checked:
            self.capture_mode = mode
            if mode == 'source':
                self.raster_viewer.hide()
                self.map_tool = CapturePointTool(self.iface.mapCanvas())
                self.map_tool.point_captured.connect(self.on_point_captured)
                self.iface.mapCanvas().setMapTool(self.map_tool)
            elif mode == 'target':
                if not self.raster_viewer.isVisible():
                    self.raster_viewer.show()
                self.map_tool = CapturePointTool(self.raster_viewer.canvas)
                self.map_tool.point_captured.connect(self.on_point_captured)
                self.raster_viewer.canvas.setMapTool(self.map_tool)
        else:
            self.capture_mode = None
            
    def on_point_captured(self, point):
        """Maneja el punto enviado por el click"""
        if self.capture_mode == 'source':
            # Add new row
            row = self.tableGCP.rowCount()
            self.tableGCP.insertRow(row)
            
            # Fill point ID
            self.tableGCP.setItem(row, 0, QTableWidgetItem(str(self.gcp_counter)))
            self.gcp_counter += 1
            
            # Fill Src X, Src Y
            self.tableGCP.setItem(row, 1, QTableWidgetItem(f"{point.x():.3f}"))
            self.tableGCP.setItem(row, 2, QTableWidgetItem(f"{point.y():.3f}"))
            
            self.tableGCP.selectRow(row)
            
        elif self.capture_mode == 'target':
            # Update currently selected row
            current_row = self.tableGCP.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "!", tr("warn_no_row"))
                self.btnCaptureTarget.setChecked(False)
                self.raster_viewer.canvas.unsetMapTool(self.map_tool)
                return
                
            self.tableGCP.setItem(current_row, 3, QTableWidgetItem(f"{point.x():.3f}"))
            self.tableGCP.setItem(current_row, 4, QTableWidgetItem(f"{point.y():.3f}"))
            
            # Auto-quit map tool after target
            self.btnCaptureTarget.setChecked(False)
            self.raster_viewer.canvas.unsetMapTool(self.map_tool)
            self.capture_mode = None
            
        # Call math function later to update RMSE
        self.update_residuals()
            
    def delete_selected_gcp(self):
        row = self.tableGCP.currentRow()
        if row >= 0:
            self.tableGCP.removeRow(row)
            self.update_residuals()

    def update_residuals(self):
        src_pts = []
        dst_pts = []
        valid_rows = []
        
        # Recolectar pares completos
        for row in range(self.tableGCP.rowCount()):
            sx = self.tableGCP.item(row, 1)
            sy = self.tableGCP.item(row, 2)
            dx = self.tableGCP.item(row, 3)
            dy = self.tableGCP.item(row, 4)
            
            if sx and sy and dx and dy:
                try:
                    src = (float(sx.text()), float(sy.text()))
                    dst = (float(dx.text()), float(dy.text()))
                    src_pts.append(src)
                    dst_pts.append(dst)
                    valid_rows.append(row)
                except ValueError:
                    continue
                    
        # Limpiar resultados previos
        for row in range(self.tableGCP.rowCount()):
            self.tableGCP.setItem(row, 5, QTableWidgetItem(""))
            self.tableGCP.setItem(row, 6, QTableWidgetItem(""))
            self.tableGCP.setItem(row, 7, QTableWidgetItem(""))
            
        self.update_markers()
            
        self.engine.load_points(src_pts, dst_pts)
        success = self.engine.calculate()
        
        if success:
            self.lblRMSE.setText(tr("rmse_value", val=self.engine.rmse))
            for i, row in enumerate(valid_rows):
                res_dx, res_dy, res_total = self.engine.residuals[i]
                self.tableGCP.setItem(row, 5, QTableWidgetItem(f"{res_dx:.3f}"))
                self.tableGCP.setItem(row, 6, QTableWidgetItem(f"{res_dy:.3f}"))
                self.tableGCP.setItem(row, 7, QTableWidgetItem(f"{res_total:.3f}"))
        else:
            self.lblRMSE.setText(tr("rmse_missing"))

    def update_markers(self):
        # Limpiar marcadores viejos
        for m in self.source_markers:
            self.iface.mapCanvas().scene().removeItem(m)
        self.source_markers.clear()
        
        for m in self.target_markers:
            self.raster_viewer.canvas.scene().removeItem(m)
        self.target_markers.clear()
        
        # Dibujar nuevos basados en la tabla
        for row in range(self.tableGCP.rowCount()):
            sx = self.tableGCP.item(row, 1)
            sy = self.tableGCP.item(row, 2)
            dx = self.tableGCP.item(row, 3)
            dy = self.tableGCP.item(row, 4)
            
            if sx and sy:
                try:
                    px, py = float(sx.text()), float(sy.text())
                    m = QgsVertexMarker(self.iface.mapCanvas())
                    m.setCenter(QgsPointXY(px, py))
                    m.setColor(Qt.red)
                    m.setIconType(QgsVertexMarker.ICON_CROSS)
                    m.setIconSize(15)
                    m.setPenWidth(2)
                    self.source_markers.append(m)
                except ValueError:
                    pass
                    
            if dx and dy:
                try:
                    px, py = float(dx.text()), float(dy.text())
                    m = QgsVertexMarker(self.raster_viewer.canvas)
                    m.setCenter(QgsPointXY(px, py))
                    m.setColor(Qt.blue)
                    m.setIconType(QgsVertexMarker.ICON_CROSS)
                    m.setIconSize(15)
                    m.setPenWidth(2)
                    self.target_markers.append(m)
                except ValueError:
                    pass

    def save_gcps(self):
        filename, _ = QFileDialog.getSaveFileName(self, tr("save_dialog_title"), "", "CSV Files (*.csv)")
        if not filename: return
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("id,source_x,source_y,target_x,target_y\n")
                for row in range(self.tableGCP.rowCount()):
                    i0 = self.tableGCP.item(row, 0)
                    i1 = self.tableGCP.item(row, 1)
                    i2 = self.tableGCP.item(row, 2)
                    i3 = self.tableGCP.item(row, 3)
                    i4 = self.tableGCP.item(row, 4)
                    
                    r_id = i0.text() if i0 else ""
                    sx = i1.text() if i1 else ""
                    sy = i2.text() if i2 else ""
                    tx = i3.text() if i3 else ""
                    ty = i4.text() if i4 else ""
                    
                    if r_id and sx and sy and tx and ty:
                        f.write(f"{r_id},{sx},{sy},{tx},{ty}\n")
            QMessageBox.information(self, "OK", tr("save_ok"))
        except Exception as e:
            QMessageBox.critical(self, "Error", tr("save_err", err=str(e)))

    def load_gcps(self):
        filename, _ = QFileDialog.getOpenFileName(self, tr("load_dialog_title"), "", "CSV Files (*.csv)")
        if not filename: return
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.tableGCP.setRowCount(0)
                self.gcp_counter = 1
                header_skipped = False
                for line in f:
                    if not header_skipped:
                        header_skipped = True
                        continue
                    parts = line.strip().split(',')
                    if len(parts) >= 5:
                        row = self.tableGCP.rowCount()
                        self.tableGCP.insertRow(row)
                        self.tableGCP.setItem(row, 0, QTableWidgetItem(parts[0]))
                        self.tableGCP.setItem(row, 1, QTableWidgetItem(parts[1]))
                        self.tableGCP.setItem(row, 2, QTableWidgetItem(parts[2]))
                        self.tableGCP.setItem(row, 3, QTableWidgetItem(parts[3]))
                        self.tableGCP.setItem(row, 4, QTableWidgetItem(parts[4]))
                        try:
                            self.gcp_counter = max(self.gcp_counter, int(parts[0]) + 1)
                        except ValueError:
                            pass
            self.update_residuals()
        except Exception as e:
            QMessageBox.critical(self, "Error", tr("load_err", err=str(e)))

    def get_source_layer(self):
        layer_id = self.cbSourceLayer.currentData()
        if not layer_id: return None
        return QgsProject.instance().mapLayer(layer_id)

    def custom_transform_geometry(self, geom):
        """Aplica la transformación Procrustes a una QgsGeometry entera usando QTransform nativo."""
        if not geom:
            return geom
            
        new_geom = QgsGeometry(geom)
        
        R = self.engine.rotation_matrix
        T = self.engine.translation_vector
        
        if R is not None and T is not None:
            # QTransform(m11, m12, m21, m22, dx, dy)
            # x' = m11*x + m21*y + dx
            # y' = m12*x + m22*y + dy
            from qgis.PyQt.QtGui import QTransform
            m11 = float(R[0, 0])
            m12 = float(R[1, 0])
            m21 = float(R[0, 1])
            m22 = float(R[1, 1])
            dx = float(T[0])
            dy = float(T[1])
            
            qtransform = QTransform(m11, m12, m21, m22, dx, dy)
            new_geom.transform(qtransform)
                
        return new_geom

    def toggle_preview(self):
        is_checked = self.btnPreview.isChecked()
        if not is_checked:
            if self.rubber_band:
                self.iface.mapCanvas().scene().removeItem(self.rubber_band)
                self.rubber_band = None
            return
            
        if self.engine.rotation_matrix is None:
            QMessageBox.warning(self, "!", tr("warn_no_calc"))
            self.btnPreview.setChecked(False)
            return
            
        layer = self.get_source_layer()
        if not layer:
            return
            
        # Crear capa fantasma
        self.rubber_band = QgsRubberBand(self.iface.mapCanvas(), layer.geometryType())
        self.rubber_band.setColor(Qt.red)
        self.rubber_band.setWidth(2)
        self.rubber_band.setFillColor(Qt.transparent)
        
        for feat in layer.getFeatures():
            geom = feat.geometry()
            new_geom = self.custom_transform_geometry(geom)
            self.rubber_band.addGeometry(new_geom, None)
            
    def apply_transformation(self):
        if self.engine.rotation_matrix is None:
            QMessageBox.warning(self, "!", tr("warn_no_transform"))
            return

        layer = self.get_source_layer()
        if not layer: return
        
        reply = QMessageBox.question(self, tr("confirm_apply_title"),
                tr("confirm_apply_body", name=layer.name()),
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                
        if reply == QMessageBox.No: return
        
        # 1. Determinar el tipo de geometría
        basic_wkb = QgsWkbTypes.flatType(layer.wkbType())
        map_type = {
            QgsWkbTypes.Point: "Point",
            QgsWkbTypes.LineString: "LineString",
            QgsWkbTypes.Polygon: "Polygon",
            QgsWkbTypes.MultiPoint: "MultiPoint",
            QgsWkbTypes.MultiLineString: "MultiLineString",
            QgsWkbTypes.MultiPolygon: "MultiPolygon"
        }
        wkb_str = map_type.get(basic_wkb, "Polygon")
        crs = layer.crs().authid()
        
        # 2. Crear nueva capa en memoria
        new_layer = QgsVectorLayer(f"{wkb_str}?crs={crs}", f"{layer.name()} {tr('layer_suffix')}", "memory")
        pr = new_layer.dataProvider()
        
        # 3. Copiar campos (sin atributos dependientes explícitos)
        pr.addAttributes(layer.fields())
        new_layer.updateFields()
        
        # 4. Copiar features con geometría transformada
        new_features = []
        for feat in layer.getFeatures():
            new_feat = QgsFeature(new_layer.fields())
            # setAttributes in QGIS expects a list, which feat.attributes() returns
            new_feat.setAttributes(feat.attributes())
            new_geom = self.custom_transform_geometry(feat.geometry())
            new_feat.setGeometry(new_geom)
            new_features.append(new_feat)
            
        pr.addFeatures(new_features)
        
        # 5. Agregar al proyecto QGIS
        QgsProject.instance().addMapLayer(new_layer)
        
        # Limpieza de UI
        if self.rubber_band:
            self.iface.mapCanvas().scene().removeItem(self.rubber_band)
            self.rubber_band = None
            self.btnPreview.setChecked(False)

        QMessageBox.information(self, tr("success_title"), tr("success_body"))

    def closeEvent(self, event):
        if self.rubber_band:
            self.iface.mapCanvas().scene().removeItem(self.rubber_band)
        
        for m in self.source_markers:
            self.iface.mapCanvas().scene().removeItem(m)
        self.source_markers.clear()
        
        for m in self.target_markers:
            self.raster_viewer.canvas.scene().removeItem(m)
        self.target_markers.clear()
        
        if self.map_tool:
            self.iface.mapCanvas().unsetMapTool(self.map_tool)
            self.raster_viewer.canvas.unsetMapTool(self.map_tool)
        self.raster_viewer.hide()
        self.closingPlugin.emit()
        event.accept()

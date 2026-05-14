# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

import os.path
from .dockwidget import RigidVectorAlignerDockWidget

class RigidVectorAlignerPlugin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor."""
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        self.actions = []
        self.menu = u'&GeoGhost: Align Microplots'
        self.toolbar = self.iface.addToolBar(u'GeoGhost')
        self.toolbar.setObjectName(u'GeoGhost')

        self.dockwidget = None

    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True, add_to_toolbar=True, status_tip=None, whats_this=None, parent=None):
        """Add a toolbar icon to the toolbar."""
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)
        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)
        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        self.add_action(
            icon_path, 
            text=u'Alinear Vectores (Cuerpo Rígido)',
            callback=self.run,
            parent=self.iface.mainWindow()
        )

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)
        
        if self.dockwidget:
            self.iface.removeDockWidget(self.dockwidget)

    def run(self):
        """Run method that loads and starts the plugin"""
        if not self.dockwidget:
            self.dockwidget = RigidVectorAlignerDockWidget(self.iface)
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

        self.dockwidget.show()

    def onClosePlugin(self):
        """Cleanup on close"""
        self.dockwidget = None

# -*- coding: utf-8 -*-

def classFactory(iface):
    """Load RigidVectorAlignerPlugin class from file plugin."""
    from .plugin import RigidVectorAlignerPlugin
    return RigidVectorAlignerPlugin(iface)

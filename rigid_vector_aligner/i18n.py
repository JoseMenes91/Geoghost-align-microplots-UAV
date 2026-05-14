# -*- coding: utf-8 -*-
"""
Módulo de internacionalización para GeoGhost: Align Microplots - UAV
Detecta el idioma de QGIS y devuelve los textos en el idioma correcto.
El nombre del plugin "GeoGhost: Align Microplots - UAV" es invariante.
"""
import locale

def get_locale():
    """Detecta el locale de QGIS leyendo la configuración QSettings o el locale del sistema."""
    try:
        from qgis.PyQt.QtCore import QSettings, QLocale
        override = QSettings().value("locale/userLocale", "")
        if override:
            lang = str(override)[:2].lower()
        else:
            lang = QLocale.system().name()[:2].lower()
    except Exception:
        lang = locale.getdefaultlocale()[0][:2].lower() if locale.getdefaultlocale()[0] else "en"
    return lang

# ─────────────────────────────────────────────────────────────
# Diccionario de traducciones
# ─────────────────────────────────────────────────────────────
_TRANSLATIONS = {
    # Panel / Títulos
    "panel_title":          {"es": "GeoGhost: Align Microplots - UAV",
                             "en": "GeoGhost: Align Microplots - UAV"},
    "viewer_title":         {"es": "GeoGhost | Visor Ortomosaico Destino",
                             "en": "GeoGhost | Destination Orthomosaic Viewer"},
    "viewer_title_layer":   {"es": "GeoGhost | Destino: {name}",
                             "en": "GeoGhost | Destination: {name}"},

    # Etiquetas de capas
    "label_source_layer":   {"es": "Capa Vectorial a Alinear (Diseño de Parcelas):",
                             "en": "Vector Layer to Align (Plot Design):"},
    "label_target_layer":   {"es": "Ortomosaico Destino Vectores (Nuevo Vuelo):",
                             "en": "Destination Orthomosaic — Vectors (New Flight):"},
    "label_viewer_combo":   {"es": "Ortomosaico de Destino (Nuevo Vuelo):",
                             "en": "Destination Orthomosaic (New Flight):"},
    "btn_open_viewer":      {"es": "Abrir Visor de Ortomosaico Destino",
                             "en": "Open Destination Orthomosaic Viewer"},
    "btn_refresh":          {"es": "Actualizar Capas",
                             "en": "Refresh Layers"},

    # Tabla GCPs
    "label_gcps":           {"es": "Puntos de Control (GCPs):",
                             "en": "Ground Control Points (GCPs):"},
    "btn_save":             {"es": "Guardar GCPs",
                             "en": "Save GCPs"},
    "btn_load":             {"es": "Cargar GCPs",
                             "en": "Load GCPs"},
    "rmse_default":         {"es": "RMSE: --",
                             "en": "RMSE: --"},
    "rmse_value":           {"es": "RMSE: {val:.3f} m",
                             "en": "RMSE: {val:.3f} m"},
    "rmse_missing":         {"es": "RMSE: -- (Faltan puntos)",
                             "en": "RMSE: -- (Need more points)"},

    # Botones acción
    "btn_capture_src":      {"es": "Capturar Puntos de Origen",
                             "en": "Capture Origin Points"},
    "btn_capture_dst":      {"es": "Capturar Puntos de Destino",
                             "en": "Capture Destination Points"},
    "btn_delete_gcp":       {"es": "Eliminar Punto",
                             "en": "Delete Point"},
    "btn_preview":          {"es": "Capa Fantasma (Vista Previa)",
                             "en": "Ghost Layer (Preview)"},
    "btn_apply":            {"es": "Aplicar Ajuste",
                             "en": "Apply Alignment"},

    # Mensajes de error / info
    "warn_no_row":          {"es": "Seleccione una fila en la tabla antes de capturar el punto de Destino.",
                             "en": "Select a row in the table before capturing the Destination point."},
    "warn_no_calc":         {"es": "Calcule primero el ajuste (RMSE) con al menos 2 puntos GCP.",
                             "en": "First calculate the alignment (RMSE) with at least 2 GCP pairs."},
    "warn_no_transform":    {"es": "Ajuste matemático no calculado o sin datos.",
                             "en": "Mathematical alignment not calculated or no data available."},
    "confirm_apply_title":  {"es": "Aplicar Transformación de Cuerpo Rígido",
                             "en": "Apply Rigid Body Transformation"},
    "confirm_apply_body":   {"es": "¿Generar una copia alineada de la capa '{name}'?\nSe creará una nueva capa temporal conservando los atributos originales.",
                             "en": "Generate an aligned copy of layer '{name}'?\nA new temporary layer will be created preserving the original attributes."},
    "layer_suffix":         {"es": "(Alineada)",
                             "en": "(Aligned)"},
    "success_title":        {"es": "Éxito",
                             "en": "Success"},
    "success_body":         {"es": "Transformación completada. Se generó una nueva capa temporal en el proyecto (recuerde exportarla si desea guardarla en disco).",
                             "en": "Transformation complete. A new temporary layer was added to the project (remember to export it if you want to save it to disk)."},
    "save_dialog_title":    {"es": "Guardar Puntos de Control",
                             "en": "Save Ground Control Points"},
    "load_dialog_title":    {"es": "Cargar Puntos de Control",
                             "en": "Load Ground Control Points"},
    "save_ok":              {"es": "Puntos guardados correctamente.",
                             "en": "Points saved successfully."},
    "save_err":             {"es": "No se pudo guardar el archivo: {err}",
                             "en": "Could not save the file: {err}"},
    "load_err":             {"es": "No se pudo cargar el archivo: {err}",
                             "en": "Could not load the file: {err}"},
}

_lang = None

def get_lang():
    global _lang
    if _lang is None:
        _lang = get_locale()
    return _lang if _lang in ("es", "en") else "en"

def tr(key, **kwargs):
    """Devuelve el string traducido para la clave dada, con formato opcional."""
    lang = get_lang()
    translations = _TRANSLATIONS.get(key, {})
    text = translations.get(lang, translations.get("en", key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text

# GeoGhost: Align Microplots - UAV

Plugin para QGIS 3 que realinea shapefiles de diseño de parcelas UAV a nuevos ortomosaicos mediante transformación de cuerpo rígido (traslación + rotación). Sin distorsión de geometría.

## ¿Para qué sirve?

Cada vez que se vuela una nueva misión UAV, el ortomosaico generado presenta un desplazamiento leve respecto al vuelo anterior. GeoGhost resuelve esto en pocos clics: se marcan pares de Puntos de Control (GCPs) — el mismo punto identificable en ambos ortomosaicos — y el plugin calcula automáticamente la traslación y rotación óptima para encajar el vector de diseño de parcelas con la nueva imagen.

Las geometrías **nunca se distorsionan**: solo se trasladan y rotan como un cuerpo rígido. El resultado es una nueva capa alineada lista para exportar, con todos los atributos originales preservados.

## Instalación

1. Copiar la carpeta `rigid_vector_aligner` en la carpeta de plugins de QGIS:
   - Windows: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
   - Linux/Mac: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
2. Reiniciar QGIS y activar el plugin desde **Complementos → Administrar e instalar complementos**.

## Uso

1. Cargar en QGIS el vector de parcelas (vuelo anterior) y el ortomosaico nuevo.
2. Abrir el panel de GeoGhost desde el menú o la barra de herramientas.
3. Seleccionar la capa vectorial a alinear y el ortomosaico de destino.
4. Capturar al menos 2 pares de GCPs (origen en el canvas principal, destino en el visor de ortomosaico).
5. Verificar el RMSE y usar **Capa Fantasma** para previsualizar.
6. Aplicar el ajuste para generar la capa alineada.

## Requisitos

- QGIS 3.0 o superior
- NumPy (incluido con QGIS)

## Autor

**José Fernando Menes**

## Licencia

MIT License — ver [LICENSE](LICENSE)

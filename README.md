# Geoghost-align-microplots-UAV-QGIS
Microplot Vector Layer Georeferencing for UAV Trials A QGIS plugin for the alignment and translation of experimental grids using control points.


<img width="500" height="500" alt="icon-removebg-preview" src="https://github.com/user-attachments/assets/2d0c51ee-bbbd-4ac9-bf14-0813058d1d73" />




QGIS 3 Plugin · UAV plot alignment via rigid body transformation

What problem does it solve?
When running multiple UAV flights over the same field trial, the orthomosaics from different dates don't land in exactly the same position. The drone GPS has inherent error, and the photogrammetric processing adds further offset. The result: the plot design shapefile that worked perfectly for the first flight no longer fits the second one.

The usual workaround is to manually move and rotate the vector layer — slow and hard to reproduce. GeoGhost automates that process.

The workflow is simple: mark the same identifiable point on both the old and the new orthomosaics, repeat that for at least 2 points, and the plugin computes the optimal translation and rotation to snap the shapefile into alignment with the new image.

How it works (the math, briefly)
GeoGhost applies a rigid body transformation: translation + rotation, no scaling, no distortion. Plot polygons keep their exact shape and size — they just move and rotate as a whole.

Internally, it uses the Procrustes algorithm (SVD — Singular Value Decomposition):

Compute centroids of the source and destination point sets.
Center each point cloud around its centroid.
Build the cross-covariance matrix between both sets.
Apply SVD to get the optimal rotation matrix.
Compute translation as the difference between transformed centroids.
The result is the rotation and translation that minimizes the RMSE across all GCP pairs. With 4 points the fit is exact.

## 🛠 Installation

1. Download or clone this repository.
2. Copy the `microplot_generator` folder into your local QGIS plugins directory: (e.g., `C:\Users\YourUser\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins`).

 <img width="651" height="341" alt="image" src="https://github.com/user-attachments/assets/06502863-1624-48f6-96f2-2e421811ab03" />
<img width="988" height="750" alt="image" src="https://github.com/user-attachments/assets/c715fc19-04e3-4601-afab-f05e53ac147a" />
<img width="839" height="262" alt="image" src="https://github.com/user-attachments/assets/69b1add6-b18a-4a74-9391-36b2198fe5ab" />




## Step-by-step tutorial

1. Set up the project
Load into QGIS the new orthomosaic (raster) and the plot shapefile (vector).

2. Open the GeoGhost panel
Click the GeoGhost icon in the toolbar, or go to GeoGhost → Align Vectors (Rigid Body).

3. Select layers
Vector Layer to Align → the plot shapefile.
Destination Orthomosaic — Vectors (New Flight) → the new flight raster.
If layers don't appear, click Refresh Layers.

4. Open the Orthomosaic Viewer
Click Open Destination Orthomosaic Viewer. A secondary window opens with an independent canvas showing the new orthomosaic. You can place it on a second monitor.

The main canvas shows the old flight (where the vector currently is); the viewer shows the new flight (where it needs to go).

5. Capture Ground Control Points (GCPs)
Find recognizable points visible in both orthomosaics 

Origin: click Capture Origin Points → click on the main canvas → a red cross appears.

Destination: click Capture Destination Points → click on the Viewer → a blue cross appears.

<img width="945" height="526" alt="image" src="https://github.com/user-attachments/assets/83d659e1-7d11-413b-b8d6-f5af3f76e533" />

Repeat this process for at least 4 points, ideally placing one in each corner of the trial to ensure a stable and uniform alignment across the entire grid."

💡 Choose points that are well spread apart. One near the center + one at a trial edge works well.


6. Preview with the Ghost Layer
Click Ghost Layer (Preview) to see the new position of all plots without changing anything yet. A red outline is overlaid on the canvas.

7. Apply the alignment
Click Apply Alignment. A new temporary layer is created, named [original name] (Aligned), with all attributes preserved.

⚠️ The layer is in memory only. To save it: right-click → Export → Save Features As...

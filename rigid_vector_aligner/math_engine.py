# -*- coding: utf-8 -*-
import numpy as np
import math

class RigidTransformEngine:
    """
    Calcula la transformación rígida óptima (traslación + rotación, sin escala)
    entre dos grupos de puntos usando SVD (Procrustes).
    """
    
    def __init__(self):
        self.points_src = []
        self.points_dst = []
        
        # Resultados de transformación
        self.rotation_matrix = None
        self.translation_vector = None
        
        # Residuales
        self.residuals = []
        self.rmse = 0.0
        
    def load_points(self, src_pts, dst_pts):
        """
        Carga puntos desde listas de tuplas [(x1,y1), (x2,y2)...]
        Deben tener el mismo conteo.
        """
        self.points_src = np.array(src_pts, dtype=np.float64)
        self.points_dst = np.array(dst_pts, dtype=np.float64)
        
    def calculate(self):
        """
        Calcula la transformación óptima de rígido (Rx + t).
        Retorna True si fue exitoso (n>=2), False en otro caso.
        """
        n = len(self.points_src)
        if n < 2 or len(self.points_dst) != n:
            self.residuals = []
            self.rmse = 0.0
            return False
            
        # 1. Encontrar los centroides
        centroid_src = np.mean(self.points_src, axis=0)
        centroid_dst = np.mean(self.points_dst, axis=0)
        
        # 2. Centrar los puntos
        src_centered = self.points_src - centroid_src
        dst_centered = self.points_dst - centroid_dst
        
        # 3. Matriz de covarianza cruzada (H = src^T * dst)
        H = np.dot(src_centered.T, dst_centered)
        
        # 4. Descomposición de valores singulares (SVD)
        U, S, Vt = np.linalg.svd(H)
        
        # 5. Calcular la matriz de rotación
        R = np.dot(Vt.T, U.T)
        
        # Prevenir reflexión (det negativo = reflexión no deseada)
        if np.linalg.det(R) < 0:
            Vt[1, :] *= -1
            R = np.dot(Vt.T, U.T)
            
        # 6. Calcular translación (t = centroid_dst - R * centroid_src)
        t = centroid_dst - np.dot(R, centroid_src)
        
        self.rotation_matrix = R
        self.translation_vector = t
        
        # 7. Calcular residuales y RMSE
        self._calculate_errors()
        return True
        
    def _calculate_errors(self):
        """
        Calcula el desplazamiento de cada punto original aplicando el modelo 
        y calculando su delta métrico final, más RMSE global.
        """
        self.residuals = []
        sum_sq_err = 0.0
        
        for i in range(len(self.points_src)):
            src_pt = self.points_src[i]
            dst_pt = self.points_dst[i]
            
            # Pto calculado: P' = R*P + t
            calc_pt = np.dot(self.rotation_matrix, src_pt) + self.translation_vector
            
            # Diferencia real
            dx = calc_pt[0] - dst_pt[0]
            dy = calc_pt[1] - dst_pt[1]
            dist_sq = dx**2 + dy**2
            residual = math.sqrt(dist_sq)
            
            self.residuals.append((dx, dy, residual))
            sum_sq_err += dist_sq
            
        self.rmse = math.sqrt(sum_sq_err / len(self.points_src))
        
    def transform_point(self, x, y):
        """Aplica la transformación rígida calculada a un pto específico."""
        if self.rotation_matrix is None:
            return x, y
        pt = np.array([x, y], dtype=np.float64)
        new_pt = np.dot(self.rotation_matrix, pt) + self.translation_vector
        return new_pt[0], new_pt[1]

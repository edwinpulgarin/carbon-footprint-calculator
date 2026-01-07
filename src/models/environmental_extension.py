"""
Extensión Ambiental de la Matriz Insumo-Producto
Implementa el análisis de huella de carbono y otros indicadores ambientales
"""
import numpy as np
from typing import Optional, Dict, List
from dataclasses import dataclass
from .input_output_matrix import InputOutputMatrix


@dataclass
class EnvironmentalIndicators:
    """Estructura para almacenar indicadores ambientales calculados"""
    direct_intensity: np.ndarray  # Intensidad ambiental directa (D)
    total_multipliers: np.ndarray  # Multiplicadores totales (D_a)
    backward_linkages: np.ndarray  # Encadenamientos hacia atrás (BL)
    forward_linkages: np.ndarray  # Encadenamientos hacia adelante (FL)
    total_emissions: np.ndarray  # Emisiones totales por indicador


class EnvironmentalExtension:
    """
    Extensión ambiental de la Matriz Insumo-Producto

    Implementa la metodología de cuentas satélite ambientales
    siguiendo las guías de Eurostat y Miller & Blair (2009)
    """

    def __init__(self, io_matrix: InputOutputMatrix,
                 environmental_pressures: np.ndarray):
        """
        Inicializa la extensión ambiental

        Args:
            io_matrix: Objeto InputOutputMatrix ya inicializado
            environmental_pressures: Matriz de presiones ambientales (m x n)
                                   m = indicadores ambientales
                                   n = sectores económicos
        """
        self.io_matrix = io_matrix
        self.D1 = np.array(environmental_pressures, dtype=float)

        # Asegurar que las matrices económicas estén calculadas
        if io_matrix.L is None:
            io_matrix.compute_all_matrices()

        self._validate_dimensions()

        # Matrices ambientales
        self.D: Optional[np.ndarray] = None  # Intensidad directa
        self.D_a: Optional[np.ndarray] = None  # Multiplicadores totales
        self.alpha: Optional[np.ndarray] = None  # Coeficientes diagonales

    def _validate_dimensions(self) -> None:
        """Valida consistencia dimensional"""
        n_sectors_env = self.D1.shape[1]
        n_sectors_io = len(self.io_matrix.x)

        if n_sectors_env != n_sectors_io:
            raise ValueError(
                f"Dimensiones inconsistentes: presiones ambientales ({n_sectors_env} sectores) "
                f"vs matriz IO ({n_sectors_io} sectores)"
            )

    def compute_direct_intensity(self) -> np.ndarray:
        """
        Calcula coeficientes de intensidad ambiental directa
        D = D1 × (X̂)^(-1)

        Returns:
            Matriz de intensidad directa (m x n)
            Unidades: presión ambiental / unidad monetaria de producción
        """
        if self.io_matrix.X_hat is None:
            self.io_matrix.compute_diagonal_output_matrix()

        X_hat_inv = np.linalg.inv(
            self.io_matrix.X_hat + np.eye(len(self.io_matrix.x)) * 1e-10
        )

        self.D = self.D1 @ X_hat_inv
        return self.D

    def compute_total_multipliers(self) -> np.ndarray:
        """
        Calcula multiplicadores ambientales totales (directos + indirectos)
        D_a = D × L

        Enfoque consumidor (responsabilidad por demanda final)

        Returns:
            Matriz de multiplicadores totales (m x n)
        """
        if self.D is None:
            self.compute_direct_intensity()

        if self.io_matrix.L is None:
            self.io_matrix.compute_leontief_inverse()

        self.D_a = self.D @ self.io_matrix.L
        return self.D_a

    def compute_environmental_matrix_extension(self) -> tuple:
        """
        Construye matrices extendidas economía-ambiente

        Returns:
            Tuple (G, H) donde:
            - G: Matriz extendida con efectos directos
            - H: Matriz extendida con efectos totales
        """
        if self.D is None:
            self.compute_direct_intensity()

        if self.D_a is None:
            self.compute_total_multipliers()

        # G: efectos directos
        G = np.vstack([self.D, self.io_matrix.L])

        # H: efectos totales
        H = np.vstack([self.D_a, self.io_matrix.L])

        return G, H

    def aggregate_greenhouse_gases(self, ghg_indices: List[int]) -> np.ndarray:
        """
        Agrega emisiones de gases de efecto invernadero

        Args:
            ghg_indices: Índices de las filas correspondientes a GEI (ej: [0, 1, 2])

        Returns:
            Vector de emisiones GEI totales por sector (n,)
        """
        return np.sum(self.D1[ghg_indices, :], axis=0)

    def compute_sector_intensity_coefficients(self,
                                             indicator_indices: List[int]) -> np.ndarray:
        """
        Calcula coeficientes de intensidad por sector (matriz diagonal)

        Args:
            indicator_indices: Índices de indicadores a agregar

        Returns:
            Matriz diagonal de intensidad (n x n)
        """
        # Sumar indicadores seleccionados
        gamma = np.sum(self.D1[indicator_indices, :], axis=0)

        # Calcular coeficientes de intensidad
        alpha = gamma / self.io_matrix.x

        # Retornar como matriz diagonal
        return np.diag(alpha)

    def compute_leontief_environmental_multipliers(self,
                                                   indicator_indices: List[int]) -> np.ndarray:
        """
        Multiplicadores ambientales tipo Leontief (backward linkages)
        Leon_amb = alpha × L

        Responde: ¿Cuánta presión ambiental genera la demanda del sector j?

        Args:
            indicator_indices: Índices de indicadores a incluir

        Returns:
            Matriz de multiplicadores Leontief (n x n)
        """
        alpha = self.compute_sector_intensity_coefficients(indicator_indices)

        if self.io_matrix.L is None:
            self.io_matrix.compute_leontief_inverse()

        return alpha @ self.io_matrix.L

    def compute_ghosh_environmental_multipliers(self,
                                                indicator_indices: List[int]) -> np.ndarray:
        """
        Multiplicadores ambientales tipo Ghosh (forward linkages)
        Ghost_amb = G × alpha^T

        Responde: ¿Cómo se distribuye la presión ambiental del sector i?

        Args:
            indicator_indices: Índices de indicadores a incluir

        Returns:
            Matriz de multiplicadores Ghosh (n x n)
        """
        alpha = self.compute_sector_intensity_coefficients(indicator_indices)

        if self.io_matrix.G is None:
            self.io_matrix.compute_ghosh_inverse()

        return self.io_matrix.G @ alpha.T

    def compute_environmental_linkages(self,
                                       indicator_indices: List[int]) -> Dict[str, np.ndarray]:
        """
        Calcula índices de encadenamiento ambiental

        Args:
            indicator_indices: Índices de indicadores a incluir

        Returns:
            Diccionario con BL (backward) y FL (forward) linkages
        """
        # Multiplicadores Leontief (backward)
        leon_amb = self.compute_leontief_environmental_multipliers(indicator_indices)

        # Multiplicadores Ghosh (forward)
        ghost_amb = self.compute_ghosh_environmental_multipliers(indicator_indices)

        n_sectors = leon_amb.shape[0]

        # Backward Linkage
        bl_avg = np.sum(leon_amb) / n_sectors
        bl = np.sum(leon_amb, axis=1) / bl_avg

        # Forward Linkage
        fl_avg = np.sum(ghost_amb) / n_sectors
        fl = np.sum(ghost_amb, axis=0) / fl_avg

        return {
            'backward_linkages': bl,
            'forward_linkages': fl,
            'leontief_multipliers': leon_amb,
            'ghosh_multipliers': ghost_amb
        }

    def compute_carbon_footprint(self,
                                final_demand: np.ndarray,
                                ghg_indices: List[int] = [0, 1, 2]) -> Dict[str, float]:
        """
        Calcula la huella de carbono para un vector de demanda final

        Args:
            final_demand: Vector de demanda final (n,)
            ghg_indices: Índices de GEI en D1 (default: primeras 3 filas)

        Returns:
            Diccionario con resultados de huella de carbono
        """
        if self.D_a is None:
            self.compute_total_multipliers()

        # Intensidad total de GEI
        ghg_intensity = np.sum(self.D_a[ghg_indices, :], axis=0)

        # Huella total
        total_footprint = np.sum(ghg_intensity * final_demand)

        # Huella por sector
        sector_footprint = ghg_intensity * final_demand

        return {
            'total_footprint': total_footprint,
            'sector_footprint': sector_footprint,
            'ghg_intensity': ghg_intensity,
            'final_demand': final_demand
        }

    def get_full_environmental_analysis(self,
                                       ghg_indices: List[int] = [0, 1, 2],
                                       other_indices: List[int] = [3, 4, 5, 6]) -> Dict:
        """
        Realiza análisis ambiental completo

        Args:
            ghg_indices: Índices de GEI
            other_indices: Índices de otros indicadores

        Returns:
            Diccionario con todos los resultados
        """
        # Cálculos básicos
        self.compute_direct_intensity()
        self.compute_total_multipliers()

        # Análisis de GEI
        ghg_linkages = self.compute_environmental_linkages(ghg_indices)

        # Análisis de otros indicadores
        other_linkages = self.compute_environmental_linkages(other_indices)

        # Emisiones totales
        total_emissions = self.D @ self.io_matrix.x

        return {
            'direct_intensity': self.D,
            'total_multipliers': self.D_a,
            'total_emissions': total_emissions,
            'ghg_analysis': ghg_linkages,
            'other_indicators_analysis': other_linkages
        }

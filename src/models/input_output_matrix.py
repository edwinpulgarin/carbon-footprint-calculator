"""
Modelo de Matriz Insumo-Producto (MIP)
Implementa el análisis económico básico de la MIP
"""
import numpy as np
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class IOMatrixData:
    """Estructura de datos para almacenar componentes de la MIP"""
    Z: np.ndarray  # Matriz de consumos intermedios
    x: np.ndarray  # Vector de producción bruta
    A: np.ndarray  # Matriz de coeficientes técnicos
    L: np.ndarray  # Matriz inversa de Leontief
    G: np.ndarray  # Matriz inversa de Ghosh


class InputOutputMatrix:
    """
    Clase para análisis de Matriz Insumo-Producto

    Implementa los métodos estándar de análisis IO según Miller & Blair (2009)
    """

    def __init__(self, intermediate_consumption: np.ndarray,
                 gross_output: np.ndarray):
        """
        Inicializa la matriz insumo-producto

        Args:
            intermediate_consumption: Matriz Z de consumos intermedios (n x n)
            gross_output: Vector x de producción bruta (n,)
        """
        self.Z = np.array(intermediate_consumption, dtype=float)
        self.x = np.array(gross_output, dtype=float)

        self._validate_dimensions()

        # Matrices calculadas
        self.X_hat: Optional[np.ndarray] = None
        self.A: Optional[np.ndarray] = None
        self.L: Optional[np.ndarray] = None
        self.B: Optional[np.ndarray] = None
        self.G: Optional[np.ndarray] = None

    def _validate_dimensions(self) -> None:
        """Valida las dimensiones de las matrices"""
        n_sectors_z = self.Z.shape[0]
        n_sectors_x = len(self.x)

        if self.Z.shape[0] != self.Z.shape[1]:
            raise ValueError("La matriz Z debe ser cuadrada")

        if n_sectors_z != n_sectors_x:
            raise ValueError(
                f"Dimensiones inconsistentes: Z({n_sectors_z}x{n_sectors_z}) "
                f"vs x({n_sectors_x})"
            )

    def compute_diagonal_output_matrix(self) -> np.ndarray:
        """
        Calcula la matriz diagonal de producción bruta (X̂)

        Returns:
            Matriz diagonal n x n
        """
        self.X_hat = np.diag(self.x)
        return self.X_hat

    def compute_technical_coefficients(self) -> np.ndarray:
        """
        Calcula la matriz de coeficientes técnicos A
        A = Z * X̂^(-1)

        Returns:
            Matriz de coeficientes técnicos (n x n)
        """
        if self.X_hat is None:
            self.compute_diagonal_output_matrix()

        # Evitar división por cero
        X_hat_inv = np.linalg.inv(self.X_hat + np.eye(len(self.x)) * 1e-10)
        self.A = self.Z @ X_hat_inv

        return self.A

    def compute_leontief_inverse(self) -> np.ndarray:
        """
        Calcula la matriz inversa de Leontief L
        L = (I - A)^(-1)

        Captura los encadenamientos hacia atrás (backward linkages)

        Returns:
            Matriz inversa de Leontief (n x n)
        """
        if self.A is None:
            self.compute_technical_coefficients()

        n = self.A.shape[0]
        I = np.eye(n)

        self.L = np.linalg.inv(I - self.A)
        return self.L

    def compute_allocation_coefficients(self) -> np.ndarray:
        """
        Calcula la matriz de coeficientes de distribución B
        B = X̂^(-1) * Z

        Returns:
            Matriz de coeficientes de distribución (n x n)
        """
        if self.X_hat is None:
            self.compute_diagonal_output_matrix()

        # Evitar división por cero usando sweep
        self.B = self.Z / self.x[:, np.newaxis]

        return self.B

    def compute_ghosh_inverse(self) -> np.ndarray:
        """
        Calcula la matriz inversa de Ghosh G
        G = (I - B)^(-1)

        Captura los encadenamientos hacia adelante (forward linkages)

        Returns:
            Matriz inversa de Ghosh (n x n)
        """
        if self.B is None:
            self.compute_allocation_coefficients()

        n = self.B.shape[0]
        I = np.eye(n)

        self.G = np.linalg.inv(I - self.B)
        return self.G

    def compute_all_matrices(self) -> IOMatrixData:
        """
        Calcula todas las matrices principales

        Returns:
            IOMatrixData con todas las matrices calculadas
        """
        self.compute_diagonal_output_matrix()
        self.compute_technical_coefficients()
        self.compute_leontief_inverse()
        self.compute_allocation_coefficients()
        self.compute_ghosh_inverse()

        return IOMatrixData(
            Z=self.Z,
            x=self.x,
            A=self.A,
            L=self.L,
            G=self.G
        )

    def get_sector_multipliers(self, sector_idx: int) -> dict:
        """
        Calcula multiplicadores para un sector específico

        Args:
            sector_idx: Índice del sector (0-based)

        Returns:
            Diccionario con multiplicadores del sector
        """
        if self.L is None:
            self.compute_leontief_inverse()

        return {
            'backward_linkage': np.sum(self.L[:, sector_idx]),
            'forward_linkage': np.sum(self.G[sector_idx, :]) if self.G is not None else None,
            'total_output_multiplier': np.sum(self.L[:, sector_idx])
        }

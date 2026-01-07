"""
Tests para InputOutputMatrix
"""
import pytest
import numpy as np
from src.models.input_output_matrix import InputOutputMatrix


class TestInputOutputMatrix:
    """Test suite para matriz insumo-producto"""

    @pytest.fixture
    def sample_data(self):
        """Datos de muestra para tests"""
        Z = np.array([
            [10, 20, 15],
            [30, 40, 25],
            [20, 30, 35]
        ], dtype=float)

        x = np.array([100, 200, 150], dtype=float)

        return Z, x

    def test_initialization(self, sample_data):
        """Test de inicialización"""
        Z, x = sample_data
        io_matrix = InputOutputMatrix(Z, x)

        assert io_matrix.Z.shape == (3, 3)
        assert len(io_matrix.x) == 3
        np.testing.assert_array_equal(io_matrix.Z, Z)
        np.testing.assert_array_equal(io_matrix.x, x)

    def test_invalid_dimensions(self):
        """Test con dimensiones inválidas"""
        Z = np.array([[10, 20], [30, 40]])
        x = np.array([100, 200, 300])  # Dimensión incorrecta

        with pytest.raises(ValueError):
            InputOutputMatrix(Z, x)

    def test_non_square_matrix(self):
        """Test con matriz no cuadrada"""
        Z = np.array([[10, 20, 30], [40, 50, 60]])
        x = np.array([100, 200])

        with pytest.raises(ValueError):
            InputOutputMatrix(Z, x)

    def test_diagonal_output_matrix(self, sample_data):
        """Test de matriz diagonal de producción"""
        Z, x = sample_data
        io_matrix = InputOutputMatrix(Z, x)

        X_hat = io_matrix.compute_diagonal_output_matrix()

        assert X_hat.shape == (3, 3)
        np.testing.assert_array_equal(np.diag(X_hat), x)
        # Verificar que es diagonal
        assert np.all(X_hat == np.diag(np.diag(X_hat)))

    def test_technical_coefficients(self, sample_data):
        """Test de coeficientes técnicos"""
        Z, x = sample_data
        io_matrix = InputOutputMatrix(Z, x)

        A = io_matrix.compute_technical_coefficients()

        assert A.shape == (3, 3)
        # Coeficientes deben ser positivos o cero
        assert np.all(A >= 0)
        # Cada columna debe sumar menos que 1 (condición de productividad)
        assert np.all(np.sum(A, axis=0) < 1)

    def test_leontief_inverse(self, sample_data):
        """Test de inversa de Leontief"""
        Z, x = sample_data
        io_matrix = InputOutputMatrix(Z, x)

        L = io_matrix.compute_leontief_inverse()

        assert L.shape == (3, 3)
        # Diagonal debe ser >= 1
        assert np.all(np.diag(L) >= 1)
        # Todos los elementos deben ser positivos
        assert np.all(L > 0)

        # Verificar propiedad: L(I-A) = I
        A = io_matrix.A
        I = np.eye(3)
        result = L @ (I - A)
        np.testing.assert_array_almost_equal(result, I, decimal=10)

    def test_ghosh_inverse(self, sample_data):
        """Test de inversa de Ghosh"""
        Z, x = sample_data
        io_matrix = InputOutputMatrix(Z, x)

        G = io_matrix.compute_ghosh_inverse()

        assert G.shape == (3, 3)
        # Diagonal debe ser >= 1
        assert np.all(np.diag(G) >= 1)
        # Todos los elementos deben ser positivos
        assert np.all(G > 0)

    def test_compute_all_matrices(self, sample_data):
        """Test de cálculo de todas las matrices"""
        Z, x = sample_data
        io_matrix = InputOutputMatrix(Z, x)

        data = io_matrix.compute_all_matrices()

        assert data.Z is not None
        assert data.x is not None
        assert data.A is not None
        assert data.L is not None
        assert data.G is not None

    def test_sector_multipliers(self, sample_data):
        """Test de multiplicadores por sector"""
        Z, x = sample_data
        io_matrix = InputOutputMatrix(Z, x)
        io_matrix.compute_all_matrices()

        multipliers = io_matrix.get_sector_multipliers(0)

        assert 'backward_linkage' in multipliers
        assert 'forward_linkage' in multipliers
        assert 'total_output_multiplier' in multipliers
        assert multipliers['backward_linkage'] > 0

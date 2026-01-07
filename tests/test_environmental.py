"""
Tests para EnvironmentalExtension
"""
import pytest
import numpy as np
from src.models.input_output_matrix import InputOutputMatrix
from src.models.environmental_extension import EnvironmentalExtension


class TestEnvironmentalExtension:
    """Test suite para extensión ambiental"""

    @pytest.fixture
    def sample_io_matrix(self):
        """Matriz IO de muestra"""
        Z = np.array([
            [10, 20, 15],
            [30, 40, 25],
            [20, 30, 35]
        ], dtype=float)

        x = np.array([100, 200, 150], dtype=float)

        io_matrix = InputOutputMatrix(Z, x)
        io_matrix.compute_all_matrices()

        return io_matrix

    @pytest.fixture
    def sample_environmental_data(self):
        """Datos ambientales de muestra"""
        # 3 indicadores x 3 sectores
        return np.array([
            [50, 100, 75],   # CO2
            [10, 20, 15],    # CH4
            [5, 10, 7.5],    # N2O
        ], dtype=float)

    def test_initialization(self, sample_io_matrix, sample_environmental_data):
        """Test de inicialización"""
        env_ext = EnvironmentalExtension(sample_io_matrix, sample_environmental_data)

        assert env_ext.D1.shape == (3, 3)
        assert env_ext.io_matrix is not None

    def test_invalid_dimensions(self, sample_io_matrix):
        """Test con dimensiones inconsistentes"""
        # 3 indicadores x 2 sectores (incorrecto)
        bad_data = np.array([
            [50, 100],
            [10, 20],
            [5, 10]
        ])

        with pytest.raises(ValueError):
            EnvironmentalExtension(sample_io_matrix, bad_data)

    def test_direct_intensity(self, sample_io_matrix, sample_environmental_data):
        """Test de intensidad directa"""
        env_ext = EnvironmentalExtension(sample_io_matrix, sample_environmental_data)

        D = env_ext.compute_direct_intensity()

        assert D.shape == (3, 3)
        # Todos los elementos deben ser >= 0
        assert np.all(D >= 0)

    def test_total_multipliers(self, sample_io_matrix, sample_environmental_data):
        """Test de multiplicadores totales"""
        env_ext = EnvironmentalExtension(sample_io_matrix, sample_environmental_data)

        D_a = env_ext.compute_total_multipliers()

        assert D_a.shape == (3, 3)
        # Multiplicadores totales deben ser >= intensidad directa
        assert np.all(D_a >= env_ext.D)

    def test_aggregate_ghg(self, sample_io_matrix, sample_environmental_data):
        """Test de agregación de GEI"""
        env_ext = EnvironmentalExtension(sample_io_matrix, sample_environmental_data)

        ghg_total = env_ext.aggregate_greenhouse_gases([0, 1, 2])

        assert len(ghg_total) == 3
        assert np.all(ghg_total > 0)
        # Debe ser la suma de las 3 filas
        expected = np.sum(sample_environmental_data, axis=0)
        np.testing.assert_array_almost_equal(ghg_total, expected)

    def test_environmental_linkages(self, sample_io_matrix, sample_environmental_data):
        """Test de encadenamientos ambientales"""
        env_ext = EnvironmentalExtension(sample_io_matrix, sample_environmental_data)

        linkages = env_ext.compute_environmental_linkages([0, 1, 2])

        assert 'backward_linkages' in linkages
        assert 'forward_linkages' in linkages
        assert 'leontief_multipliers' in linkages
        assert 'ghosh_multipliers' in linkages

        assert len(linkages['backward_linkages']) == 3
        assert len(linkages['forward_linkages']) == 3

    def test_carbon_footprint(self, sample_io_matrix, sample_environmental_data):
        """Test de cálculo de huella de carbono"""
        env_ext = EnvironmentalExtension(sample_io_matrix, sample_environmental_data)
        env_ext.compute_total_multipliers()

        final_demand = np.array([50, 100, 75])

        footprint = env_ext.compute_carbon_footprint(final_demand, ghg_indices=[0, 1, 2])

        assert 'total_footprint' in footprint
        assert 'sector_footprint' in footprint
        assert 'ghg_intensity' in footprint

        assert footprint['total_footprint'] > 0
        assert len(footprint['sector_footprint']) == 3

    def test_full_analysis(self, sample_io_matrix, sample_environmental_data):
        """Test de análisis completo"""
        env_ext = EnvironmentalExtension(sample_io_matrix, sample_environmental_data)

        results = env_ext.get_full_environmental_analysis(
            ghg_indices=[0, 1, 2],
            other_indices=[]
        )

        assert 'direct_intensity' in results
        assert 'total_multipliers' in results
        assert 'total_emissions' in results
        assert 'ghg_analysis' in results

"""
Servicio de cálculo de Huella de Carbono
"""
import numpy as np
from typing import Dict, List, Optional
from ..models.input_output_matrix import InputOutputMatrix
from ..models.environmental_extension import EnvironmentalExtension


class CarbonFootprintCalculator:
    """
    Calculadora de Huella de Carbono usando metodología IO

    Proporciona métodos de alto nivel para calcular huellas de carbono
    de productos, sectores y demanda final
    """

    def __init__(self,
                 io_matrix: InputOutputMatrix,
                 env_extension: EnvironmentalExtension,
                 ghg_indices: List[int] = [0, 1, 2]):
        """
        Inicializa la calculadora

        Args:
            io_matrix: Matriz insumo-producto
            env_extension: Extensión ambiental
            ghg_indices: Índices de GEI en la matriz ambiental (default: [0,1,2])
        """
        self.io_matrix = io_matrix
        self.env_extension = env_extension
        self.ghg_indices = ghg_indices

        # Calcular multiplicadores si no están calculados
        if env_extension.D_a is None:
            env_extension.compute_total_multipliers()

    def calculate_product_footprint(self,
                                   sector_idx: int,
                                   quantity: float = 1.0,
                                   unit: str = "monetary") -> Dict:
        """
        Calcula la huella de carbono de un producto específico

        Args:
            sector_idx: Índice del sector productor
            quantity: Cantidad demandada
            unit: Unidad de medida ("monetary" para unidades monetarias)

        Returns:
            Diccionario con resultados de huella
        """
        # Vector de demanda final (solo el sector seleccionado)
        final_demand = np.zeros(len(self.io_matrix.x))
        final_demand[sector_idx] = quantity

        # Intensidad GEI del sector
        ghg_intensity = np.sum(
            self.env_extension.D_a[self.ghg_indices, sector_idx]
        )

        # Producción total requerida
        total_production = self.io_matrix.L @ final_demand

        # Emisiones por sector en la cadena
        sector_emissions = np.sum(
            self.env_extension.D[self.ghg_indices, :],
            axis=0
        ) * total_production

        return {
            'sector_index': sector_idx,
            'quantity': quantity,
            'unit': unit,
            'direct_intensity': ghg_intensity,
            'total_footprint': np.sum(sector_emissions),
            'emissions_by_sector': sector_emissions,
            'total_production_required': total_production,
            'direct_emissions': sector_emissions[sector_idx],
            'indirect_emissions': np.sum(sector_emissions) - sector_emissions[sector_idx]
        }

    def calculate_basket_footprint(self,
                                  demand_vector: np.ndarray,
                                  basket_name: str = "Custom basket") -> Dict:
        """
        Calcula la huella de una canasta de consumo

        Args:
            demand_vector: Vector de demanda final (n,)
            basket_name: Nombre descriptivo de la canasta

        Returns:
            Diccionario con resultados
        """
        # Producción total requerida
        total_production = self.io_matrix.L @ demand_vector

        # Intensidad GEI por sector
        ghg_intensity = np.sum(
            self.env_extension.D_a[self.ghg_indices, :],
            axis=0
        )

        # Emisiones por sector
        sector_emissions = np.sum(
            self.env_extension.D[self.ghg_indices, :],
            axis=0
        ) * total_production

        # Contribución de cada demanda final
        demand_contribution = ghg_intensity * demand_vector

        return {
            'basket_name': basket_name,
            'total_footprint': np.sum(sector_emissions),
            'emissions_by_sector': sector_emissions,
            'demand_contribution': demand_contribution,
            'total_production': total_production,
            'ghg_intensity': ghg_intensity,
            'top_emitters': self._get_top_contributors(sector_emissions, n=5)
        }

    def calculate_sector_responsibility(self,
                                       sector_idx: int) -> Dict:
        """
        Calcula la responsabilidad ambiental de un sector
        (enfoque productor vs consumidor)

        Args:
            sector_idx: Índice del sector

        Returns:
            Diccionario con análisis de responsabilidad
        """
        # Responsabilidad del productor (emisiones directas)
        producer_responsibility = np.sum(
            self.env_extension.D[self.ghg_indices, sector_idx]
        ) * self.io_matrix.x[sector_idx]

        # Responsabilidad del consumidor (emisiones por demanda)
        consumer_responsibility = np.sum(
            self.env_extension.D_a[self.ghg_indices, sector_idx]
        )

        # Encadenamientos
        linkages = self.env_extension.compute_environmental_linkages(self.ghg_indices)

        return {
            'sector_index': sector_idx,
            'producer_responsibility': producer_responsibility,
            'consumer_responsibility': consumer_responsibility,
            'backward_linkage': linkages['backward_linkages'][sector_idx],
            'forward_linkage': linkages['forward_linkages'][sector_idx],
            'linkage_type': self._classify_linkage(
                linkages['backward_linkages'][sector_idx],
                linkages['forward_linkages'][sector_idx]
            )
        }

    def compare_scenarios(self,
                         baseline: np.ndarray,
                         alternative: np.ndarray,
                         scenario_names: tuple = ("Baseline", "Alternative")) -> Dict:
        """
        Compara huellas de carbono entre dos escenarios

        Args:
            baseline: Vector de demanda del escenario base
            alternative: Vector de demanda del escenario alternativo
            scenario_names: Nombres de los escenarios

        Returns:
            Diccionario con comparación
        """
        footprint_baseline = self.calculate_basket_footprint(
            baseline,
            scenario_names[0]
        )

        footprint_alternative = self.calculate_basket_footprint(
            alternative,
            scenario_names[1]
        )

        # Calcular diferencias
        emission_diff = (
            footprint_alternative['total_footprint'] -
            footprint_baseline['total_footprint']
        )

        percent_change = (
            emission_diff / footprint_baseline['total_footprint'] * 100
        )

        sector_diff = (
            footprint_alternative['emissions_by_sector'] -
            footprint_baseline['emissions_by_sector']
        )

        return {
            'baseline': footprint_baseline,
            'alternative': footprint_alternative,
            'absolute_difference': emission_diff,
            'percent_change': percent_change,
            'sector_differences': sector_diff,
            'sectors_with_largest_reductions': self._get_top_contributors(
                -sector_diff, n=5
            ),
            'sectors_with_largest_increases': self._get_top_contributors(
                sector_diff, n=5
            )
        }

    def get_mitigation_priorities(self,
                                  demand_vector: np.ndarray,
                                  n_priorities: int = 10) -> List[Dict]:
        """
        Identifica prioridades de mitigación basadas en contribución a emisiones

        Args:
            demand_vector: Vector de demanda final
            n_priorities: Número de sectores prioritarios

        Returns:
            Lista de sectores prioritarios con métricas
        """
        # Calcular huella
        footprint = self.calculate_basket_footprint(demand_vector)

        # Encadenamientos
        linkages = self.env_extension.compute_environmental_linkages(self.ghg_indices)

        # Crear lista de prioridades
        priorities = []

        top_sectors = self._get_top_contributors(
            footprint['emissions_by_sector'],
            n=n_priorities
        )

        for sector_info in top_sectors:
            idx = sector_info['index']

            priorities.append({
                'sector_index': idx,
                'emissions': sector_info['value'],
                'percent_of_total': sector_info['percent'],
                'backward_linkage': linkages['backward_linkages'][idx],
                'forward_linkage': linkages['forward_linkages'][idx],
                'direct_intensity': np.sum(
                    self.env_extension.D[self.ghg_indices, idx]
                ),
                'mitigation_potential': self._assess_mitigation_potential(
                    idx,
                    footprint,
                    linkages
                )
            })

        return priorities

    def _get_top_contributors(self,
                             values: np.ndarray,
                             n: int = 5) -> List[Dict]:
        """
        Obtiene los n mayores contribuyentes

        Args:
            values: Vector de valores
            n: Número de top contribuyentes

        Returns:
            Lista ordenada de contribuyentes
        """
        total = np.sum(values)
        indices = np.argsort(values)[::-1][:n]

        return [
            {
                'index': int(idx),
                'value': float(values[idx]),
                'percent': float(values[idx] / total * 100) if total > 0 else 0
            }
            for idx in indices
        ]

    def _classify_linkage(self, bl: float, fl: float) -> str:
        """
        Clasifica un sector según sus encadenamientos

        Args:
            bl: Backward linkage
            fl: Forward linkage

        Returns:
            Clasificación del sector
        """
        if bl > 1 and fl > 1:
            return "Key sector (high BL & FL)"
        elif bl > 1:
            return "Backward-driven sector"
        elif fl > 1:
            return "Forward-driven sector"
        else:
            return "Low linkage sector"

    def _assess_mitigation_potential(self,
                                    sector_idx: int,
                                    footprint: Dict,
                                    linkages: Dict) -> str:
        """
        Evalúa el potencial de mitigación de un sector

        Args:
            sector_idx: Índice del sector
            footprint: Resultados de huella
            linkages: Encadenamientos

        Returns:
            Evaluación cualitativa del potencial
        """
        emissions = footprint['emissions_by_sector'][sector_idx]
        bl = linkages['backward_linkages'][sector_idx]
        fl = linkages['forward_linkages'][sector_idx]

        # Sector clave con altas emisiones
        if bl > 1 and fl > 1 and emissions > np.mean(footprint['emissions_by_sector']):
            return "Very High - Key sector with high emissions"

        # Alto backward linkage
        elif bl > 1.5:
            return "High - Reducing demand has multiplier effects"

        # Alto forward linkage
        elif fl > 1.5:
            return "High - Decarbonizing benefits multiple sectors"

        # Altas emisiones pero bajos linkages
        elif emissions > np.mean(footprint['emissions_by_sector']):
            return "Medium - High emitter but limited spillovers"

        else:
            return "Low - Limited impact potential"

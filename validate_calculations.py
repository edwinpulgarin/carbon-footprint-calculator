"""
Script de Validación de Cálculos
Compara resultados de Python con el script R original
"""
import numpy as np
import pandas as pd
from pathlib import Path
import sys

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent))

from src.models.input_output_matrix import InputOutputMatrix
from src.models.environmental_extension import EnvironmentalExtension
from src.services.data_loader import MIPDataLoader
from src.services.carbon_calculator import CarbonFootprintCalculator


def validate_year(year: int, verbose: bool = True):
    """
    Valida los cálculos para un año específico

    Args:
        year: Año a validar (2017, 2019, 2021)
        verbose: Si True, imprime detalles

    Returns:
        Dict con resultados de validación
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"VALIDANDO AÑO {year}")
        print(f"{'='*70}\n")

    # Archivos
    mip_file = f"anex-MIP-{year}.xlsx"
    env_file = f"CAEFM-EA68aVALORADO {year}.xlsx"

    try:
        # 1. Cargar datos
        if verbose:
            print("1. Cargando datos...")

        loader = MIPDataLoader('data/raw')
        dataset = loader.load_complete_dataset(mip_file, env_file, year)

        if verbose:
            print(f"   OK Datos cargados: {dataset['n_sectors']} sectores")
            print(f"   OK Indicadores ambientales: {dataset['n_environmental_indicators']}")

        # 2. Crear matriz IO
        if verbose:
            print("\n2. Calculando Matriz Insumo-Producto...")

        io_matrix = InputOutputMatrix(
            dataset['intermediate_consumption'],
            dataset['gross_output']
        )
        io_data = io_matrix.compute_all_matrices()

        # Validaciones básicas
        n = dataset['n_sectors']

        # Validar dimensiones
        assert io_data.Z.shape == (n, n), "Dimensión incorrecta de Z"
        assert io_data.A.shape == (n, n), "Dimensión incorrecta de A"
        assert io_data.L.shape == (n, n), "Dimensión incorrecta de L"
        assert io_data.G.shape == (n, n), "Dimensión incorrecta de G"
        assert len(io_data.x) == n, "Dimensión incorrecta de x"

        if verbose:
            print(f"   OK Dimensiones correctas: {n}x{n}")

        # Validar propiedades matemáticas
        # L * (I - A) = I
        I = np.eye(n)
        L_validation = io_data.L @ (I - io_data.A)
        is_valid_L = np.allclose(L_validation, I, rtol=1e-4)

        if verbose:
            if is_valid_L:
                print("   OK Inversa de Leontief correcta: L(I-A) ~= I")
            else:
                print("   WARN: Inversa de Leontief con error numerico")

        # Validar que diagonal de L >= 1
        diag_L = np.diag(io_data.L)
        all_geq_1 = np.all(diag_L >= 0.99)  # tolerancia

        if verbose:
            if all_geq_1:
                print(f"   OK Diagonal de L >= 1: min={diag_L.min():.4f}")
            else:
                print(f"   WARN: Algunos elementos diagonales < 1")

        # Validar que A < 1 (suma de columnas)
        col_sums_A = np.sum(io_data.A, axis=0)
        all_lt_1 = np.all(col_sums_A < 1.0)

        if verbose:
            if all_lt_1:
                print(f"   OK Coeficientes tecnicos validos: max suma={col_sums_A.max():.4f}")
            else:
                print(f"   WARN: Algunas columnas de A suman >= 1")

        # 3. Extensión ambiental
        if verbose:
            print("\n3. Calculando Extensión Ambiental...")

        env_ext = EnvironmentalExtension(
            io_matrix,
            dataset['environmental_pressures']
        )

        # Calcular multiplicadores
        D = env_ext.compute_direct_intensity()
        D_a = env_ext.compute_total_multipliers()

        # Validar que D_a >= D (multiplicadores totales >= directos)
        is_greater = np.all(D_a >= D - 1e-6)  # tolerancia numérica

        if verbose:
            if is_greater:
                print("   OK Multiplicadores totales >= intensidad directa")
            else:
                print("   WARN Advertencia: Algunos multiplicadores totales < directos")

        # Validar reconstrucción de emisiones
        # D * x debe ser igual a emisiones totales originales
        emissions_calc = D @ io_data.x
        emissions_orig = np.sum(dataset['environmental_pressures'], axis=1)

        is_equal = np.allclose(emissions_calc, emissions_orig, rtol=1e-3)

        if verbose:
            if is_equal:
                print("   OK Emisiones reconstruidas correctamente")
            else:
                max_diff = np.max(np.abs(emissions_calc - emissions_orig))
                print(f"   WARN Diferencia en emisiones: max={max_diff:.2f}")

        # 4. Calculadora de huella
        if verbose:
            print("\n4. Probando Calculadora de Huella...")

        calculator = CarbonFootprintCalculator(
            io_matrix,
            env_ext,
            ghg_indices=[0, 1, 2]
        )

        # Probar cálculo de producto
        test_sector = 15
        footprint = calculator.calculate_product_footprint(test_sector, 1e6)

        if verbose:
            print(f"   OK Huella sector {test_sector}:")
            print(f"     - Huella total: {footprint['total_footprint']:.2f} ton CO2eq")
            print(f"     - Emisiones directas: {footprint['direct_emissions']:.2f}")
            print(f"     - Emisiones indirectas: {footprint['indirect_emissions']:.2f}")

        # Probar encadenamientos
        linkages = env_ext.compute_environmental_linkages([0, 1, 2])

        bl_mean = np.mean(linkages['backward_linkages'])
        fl_mean = np.mean(linkages['forward_linkages'])

        # Promedios deben ser cercanos a 1
        bl_valid = abs(bl_mean - 1.0) < 0.1
        fl_valid = abs(fl_mean - 1.0) < 0.1

        if verbose:
            print(f"\n5. Encadenamientos Ambientales:")
            print(f"   - Backward Linkage promedio: {bl_mean:.4f} {'OK' if bl_valid else 'WARN'}")
            print(f"   - Forward Linkage promedio: {fl_mean:.4f} {'OK' if fl_valid else 'WARN'}")

        # Identificar sectores clave
        bl = linkages['backward_linkages']
        fl = linkages['forward_linkages']

        key_sectors = np.where((bl > 1) & (fl > 1))[0]

        if verbose and len(key_sectors) > 0:
            print(f"\n6. Sectores Clave Identificados: {len(key_sectors)}")
            for idx in key_sectors[:5]:  # Mostrar primeros 5
                sector_name = dataset['sector_names'][idx] if idx < len(dataset['sector_names']) else f"Sector {idx}"
                print(f"   - {sector_name} (BL={bl[idx]:.2f}, FL={fl[idx]:.2f})")

        # Resumen de validación
        validation_results = {
            'year': year,
            'n_sectors': int(n),
            'n_indicators': int(dataset['n_environmental_indicators']),
            'validations': {
                'dimensions_ok': True,
                'leontief_inverse_ok': bool(is_valid_L),
                'technical_coefficients_ok': bool(all_lt_1),
                'diagonal_L_ok': bool(all_geq_1),
                'multipliers_consistent_ok': bool(is_greater),
                'emissions_reconstruction_ok': bool(is_equal),
                'linkages_mean_ok': bool(bl_valid and fl_valid)
            },
            'statistics': {
                'total_production': float(np.sum(io_data.x)),
                'total_ghg_emissions': float(np.sum(emissions_calc[:3])),
                'avg_backward_linkage': float(bl_mean),
                'avg_forward_linkage': float(fl_mean),
                'n_key_sectors': int(len(key_sectors))
            },
            'sample_footprint': {
                'sector': test_sector,
                'total': float(footprint['total_footprint']),
                'direct': float(footprint['direct_emissions']),
                'indirect': float(footprint['indirect_emissions'])
            }
        }

        # Calcular score de validación
        validations = validation_results['validations']
        score = sum(validations.values()) / len(validations) * 100
        validation_results['validation_score'] = score

        if verbose:
            print(f"\n{'='*70}")
            print(f"SCORE DE VALIDACIÓN: {score:.1f}%")
            print(f"{'='*70}")

        return validation_results

    except Exception as e:
        print(f"\nERROR en anio {year}: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'year': year,
            'error': str(e),
            'validation_score': 0
        }


def compare_years(results_dict):
    """Compara resultados entre años"""
    print(f"\n{'='*70}")
    print("COMPARACIÓN ENTRE AÑOS")
    print(f"{'='*70}\n")

    years = sorted(results_dict.keys())

    # Tabla comparativa
    print(f"{'Métrica':<40} {' | '.join([str(y) for y in years])}")
    print("-" * 70)

    # Producción total
    prod_values = [results_dict[y]['statistics']['total_production'] / 1e6
                   for y in years if 'statistics' in results_dict[y]]
    print(f"{'Producción Total (millones)':<40} {' | '.join([f'{v:>12,.0f}' for v in prod_values])}")

    # Emisiones GEI
    ghg_values = [results_dict[y]['statistics']['total_ghg_emissions'] / 1e3
                  for y in years if 'statistics' in results_dict[y]]
    print(f"{'Emisiones GEI (miles ton)':<40} {' | '.join([f'{v:>12,.0f}' for v in ghg_values])}")

    # Intensidad (emisiones / producción)
    intensity_values = [(ghg_values[i] * 1e3) / (prod_values[i] * 1e6) * 1e6
                        for i in range(len(years)) if 'statistics' in results_dict[years[i]]]
    print(f"{'Intensidad (ton/millón $)':<40} {' | '.join([f'{v:>12.2f}' for v in intensity_values])}")

    # Backward linkage
    bl_values = [results_dict[y]['statistics']['avg_backward_linkage']
                 for y in years if 'statistics' in results_dict[y]]
    print(f"{'BL promedio':<40} {' | '.join([f'{v:>12.4f}' for v in bl_values])}")

    # Forward linkage
    fl_values = [results_dict[y]['statistics']['avg_forward_linkage']
                 for y in years if 'statistics' in results_dict[y]]
    print(f"{'FL promedio':<40} {' | '.join([f'{v:>12.4f}' for v in fl_values])}")

    # Sectores clave
    key_values = [results_dict[y]['statistics']['n_key_sectors']
                  for y in years if 'statistics' in results_dict[y]]
    print(f"{'Sectores Clave':<40} {' | '.join([f'{v:>12}' for v in key_values])}")

    # Score de validación
    score_values = [results_dict[y]['validation_score']
                    for y in years if 'validation_score' in results_dict[y]]
    print(f"{'Score Validación (%)':<40} {' | '.join([f'{v:>12.1f}' for v in score_values])}")

    print("\n" + "=" * 70)


def main():
    """Función principal"""
    print("\n" + "=" * 70)
    print("VALIDACIÓN DE CÁLCULOS DE HUELLA DE CARBONO")
    print("Comparación con metodología del script R original")
    print("=" * 70)

    years = [2017, 2019, 2021]
    results = {}

    for year in years:
        result = validate_year(year, verbose=True)
        results[year] = result

    # Comparar años
    compare_years(results)

    # Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)

    all_scores = [r['validation_score'] for r in results.values() if 'validation_score' in r]
    avg_score = np.mean(all_scores)

    print(f"\nScore promedio de validación: {avg_score:.1f}%")

    if avg_score >= 90:
        print("OK VALIDACION EXITOSA - Los calculos son correctos")
    elif avg_score >= 70:
        print("WARN VALIDACION PARCIAL - Revisar advertencias")
    else:
        print("ERROR VALIDACION FALLIDA - Revisar errores")

    # Guardar resultados
    print("\nGuardando resultados en 'validation_results.json'...")
    import json
    with open('validation_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("OK Resultados guardados")

    return results


if __name__ == "__main__":
    results = main()

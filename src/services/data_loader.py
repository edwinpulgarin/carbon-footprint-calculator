"""
Servicio de carga de datos desde archivos Excel
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional


class MIPDataLoader:
    """Cargador de datos de Matriz Insumo-Producto desde archivos Excel del DANE"""

    def __init__(self, data_dir: str = "data/raw"):
        """
        Inicializa el cargador de datos

        Args:
            data_dir: Directorio donde se encuentran los archivos de datos
        """
        self.data_dir = Path(data_dir)

    def load_mip_matrix(self,
                       filename: str,
                       year: int,
                       sheet: str = "Cuadro 7",
                       skip_rows: int = 11) -> Tuple[np.ndarray, np.ndarray]:
        """
        Carga la matriz insumo-producto desde archivo Excel

        Args:
            filename: Nombre del archivo Excel
            year: Año de la MIP
            sheet: Nombre de la hoja (default: "Cuadro 7")
            skip_rows: Filas a omitir (default: 11)

        Returns:
            Tuple (Z, x) donde:
            - Z: Matriz de consumos intermedios (68 x 68)
            - x: Vector de producción bruta (68,)
        """
        filepath = self.data_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {filepath}")

        # Cargar datos
        df = pd.read_excel(filepath, sheet_name=sheet, header=0, skiprows=skip_rows)

        # Eliminar primera fila sobrante
        df = df.iloc[1:]

        # Matriz de consumos intermedios Z (68 sectores x 68 sectores)
        # Asumiendo que las columnas 2-69 contienen los datos
        Z = df.iloc[0:68, 2:70].values.astype(float)

        # Vector de producción bruta x
        # Asumiendo que la columna ...76 contiene la producción bruta
        x = df.iloc[0:68].iloc[:, 75].values.astype(float)

        return Z, x

    def load_environmental_accounts(self,
                                   filename: str,
                                   year: int,
                                   sheet: Optional[str] = None) -> np.ndarray:
        """
        Carga las cuentas ambientales

        Args:
            filename: Nombre del archivo Excel
            year: Año de las cuentas
            sheet: Nombre de la hoja (si None, usa el año como nombre)

        Returns:
            Matriz de presiones ambientales (m x n)
            m = indicadores ambientales, n = sectores
        """
        filepath = self.data_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {filepath}")

        sheet_name = sheet if sheet else str(year)

        # Cargar datos sin headers
        df = pd.read_excel(filepath, sheet_name=sheet_name, header=None)

        # La estructura es:
        # Fila 0: Título general
        # Fila 1: Códigos CIIU
        # Fila 2: Nombres de sectores
        # Fila 3+: Datos numéricos de indicadores ambientales

        # Extraer solo las filas de datos (desde fila 3) y columnas de sectores (desde columna 2)
        start_row = 3
        data_rows = []

        for idx in range(start_row, min(start_row + 20, len(df))):  # Máximo 20 indicadores
            try:
                # Intentar convertir la fila a numéricos (excluyendo primeras 2 columnas)
                row_data = pd.to_numeric(df.iloc[idx, 2:70], errors='coerce')

                # Si más del 50% son NaN, probablemente no es una fila de datos
                if row_data.notna().sum() / len(row_data) > 0.5:
                    data_rows.append(row_data.values)
                else:
                    break
            except:
                break

        if len(data_rows) == 0:
            raise ValueError(f"No se pudieron extraer datos numéricos del archivo {filename}")

        # Convertir a matriz numpy
        env_data = np.array(data_rows, dtype=float)

        # Asegurarse de que tiene 68 columnas (sectores)
        if env_data.shape[1] > 68:
            env_data = env_data[:, :68]

        return env_data

    def load_domestic_imports_matrices(self,
                                      filename: str,
                                      domestic_sheet: str = "Cuadro 5",
                                      imports_sheet: str = "Cuadro 6",
                                      skip_rows: int = 11) -> Tuple[np.ndarray, np.ndarray]:
        """
        Carga matrices de producción doméstica e importaciones

        Args:
            filename: Nombre del archivo Excel
            domestic_sheet: Hoja de producción doméstica
            imports_sheet: Hoja de importaciones
            skip_rows: Filas a omitir

        Returns:
            Tuple (Bd, Bm) donde:
            - Bd: Matriz de coeficientes domésticos (68 x 68)
            - Bm: Matriz de coeficientes importados (68 x 68)
        """
        filepath = self.data_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {filepath}")

        # Cargar producción doméstica
        df_domestic = pd.read_excel(filepath, sheet_name=domestic_sheet,
                                    header=0, skiprows=skip_rows)
        df_domestic = df_domestic.iloc[1:]
        Bd = df_domestic.iloc[0:68, 2:70].values.astype(float)

        # Cargar importaciones
        df_imports = pd.read_excel(filepath, sheet_name=imports_sheet,
                                   header=0, skiprows=skip_rows)
        df_imports = df_imports.iloc[1:]
        Bm = df_imports.iloc[0:68, 2:70].values.astype(float)

        return Bd, Bm

    def get_sector_names(self,
                        filename: str,
                        sheet: str = "Cuadro 7",
                        skip_rows: int = 11) -> list:
        """
        Extrae los nombres de los sectores

        Args:
            filename: Nombre del archivo Excel
            sheet: Nombre de la hoja
            skip_rows: Filas a omitir

        Returns:
            Lista con nombres de sectores
        """
        filepath = self.data_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {filepath}")

        df = pd.read_excel(filepath, sheet_name=sheet, header=0, skiprows=skip_rows)
        df = df.iloc[1:]

        # Asumiendo que la segunda columna contiene los nombres
        sector_names = df.iloc[0:68, 1].tolist()

        return sector_names

    def load_complete_dataset(self,
                             mip_filename: str,
                             env_filename: str,
                             year: int) -> dict:
        """
        Carga el conjunto completo de datos para análisis

        Args:
            mip_filename: Archivo de MIP
            env_filename: Archivo de cuentas ambientales
            year: Año de análisis

        Returns:
            Diccionario con todos los datos cargados
        """
        # Cargar MIP básica
        Z, x = self.load_mip_matrix(mip_filename, year)

        # Cargar cuentas ambientales
        env_data = self.load_environmental_accounts(env_filename, year)

        # Cargar doméstico/importado
        Bd, Bm = self.load_domestic_imports_matrices(mip_filename)

        # Nombres de sectores
        sector_names = self.get_sector_names(mip_filename)

        return {
            'intermediate_consumption': Z,
            'gross_output': x,
            'environmental_pressures': env_data,
            'domestic_matrix': Bd,
            'imports_matrix': Bm,
            'sector_names': sector_names,
            'year': year,
            'n_sectors': len(x),
            'n_environmental_indicators': env_data.shape[0]
        }

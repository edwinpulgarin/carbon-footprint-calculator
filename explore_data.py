"""Script para explorar la estructura de los archivos de datos"""
import pandas as pd
import sys

def explore_excel(filename, sheet_name=None):
    """Explora estructura de archivo Excel"""
    print(f"\n{'='*70}")
    print(f"Explorando: {filename}")
    print(f"{'='*70}\n")

    try:
        # Listar hojas
        xl = pd.ExcelFile(filename)
        print(f"Hojas disponibles: {xl.sheet_names}\n")

        # Si no se especifica hoja, usar la primera o la que contenga el año
        if sheet_name is None:
            # Buscar hoja con año
            for sn in xl.sheet_names:
                if any(year in str(sn) for year in ['2017', '2019', '2021']):
                    sheet_name = sn
                    break
            if sheet_name is None:
                sheet_name = xl.sheet_names[0]

        print(f"Usando hoja: '{sheet_name}'\n")

        # Leer primeras filas
        df = pd.read_excel(filename, sheet_name=sheet_name, header=None)

        print(f"Dimensiones: {df.shape}")
        print(f"\nPrimeras 15 filas:\n")
        print(df.head(15).to_string())

        print(f"\n\nÚltimas 5 columnas de las primeras 15 filas:\n")
        print(df.iloc[:15, -5:].to_string())

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Explorar archivos ambientales
    for year in [2017, 2019, 2021]:
        explore_excel(f"data/raw/CAEFM-EA68aVALORADO {year}.xlsx")

    # Explorar una MIP
    print("\n\n" + "="*70)
    print("EXPLORANDO ARCHIVO MIP 2021")
    print("="*70)
    explore_excel("data/raw/anex-MIP-2021.xlsx", "Cuadro 7")

"""
API REST para Cálculo de Huella de Carbono
Framework: FastAPI
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import numpy as np
from pathlib import Path

from ..models.input_output_matrix import InputOutputMatrix
from ..models.environmental_extension import EnvironmentalExtension
from ..services.data_loader import MIPDataLoader
from ..services.carbon_calculator import CarbonFootprintCalculator


# Modelos Pydantic para validación
class DemandVector(BaseModel):
    """Modelo para vector de demanda final"""
    values: List[float] = Field(..., description="Vector de demanda por sector")
    sector_names: Optional[List[str]] = Field(None, description="Nombres de sectores")

    class Config:
        json_schema_extra = {
            "example": {
                "values": [1000000, 500000, 750000],
                "sector_names": ["Agricultura", "Manufactura", "Servicios"]
            }
        }


class ProductFootprintRequest(BaseModel):
    """Request para huella de producto"""
    sector_index: int = Field(..., ge=0, lt=68, description="Índice del sector (0-67)")
    quantity: float = Field(..., gt=0, description="Cantidad demandada")
    unit: str = Field(default="monetary", description="Unidad de medida")

    class Config:
        json_schema_extra = {
            "example": {
                "sector_index": 15,
                "quantity": 1000000,
                "unit": "monetary"
            }
        }


class BasketFootprintRequest(BaseModel):
    """Request para huella de canasta"""
    demand_vector: List[float] = Field(..., description="Vector de demanda (68 elementos)")
    basket_name: Optional[str] = Field("Custom basket", description="Nombre de la canasta")

    class Config:
        json_schema_extra = {
            "example": {
                "demand_vector": [100000] * 68,
                "basket_name": "Canasta básica familiar"
            }
        }


class ScenarioComparisonRequest(BaseModel):
    """Request para comparación de escenarios"""
    baseline: List[float] = Field(..., description="Demanda escenario base")
    alternative: List[float] = Field(..., description="Demanda escenario alternativo")
    scenario_names: Optional[List[str]] = Field(
        ["Baseline", "Alternative"],
        description="Nombres de escenarios"
    )


class HealthResponse(BaseModel):
    """Response del endpoint de salud"""
    status: str
    version: str
    data_loaded: bool
    n_sectors: Optional[int]
    n_environmental_indicators: Optional[int]


# Inicializar FastAPI
app = FastAPI(
    title="Carbon Footprint Calculator API",
    description="API REST para cálculo de Huella de Carbono usando Análisis Insumo-Producto",
    version="1.0.0",
    contact={
        "name": "Carbon Footprint Team",
        "email": "contact@carbonfootprint.example.com"
    },
    license_info={
        "name": "MIT License"
    }
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales para objetos cargados
io_matrix: Optional[InputOutputMatrix] = None
env_extension: Optional[EnvironmentalExtension] = None
calculator: Optional[CarbonFootprintCalculator] = None
sector_names: Optional[List[str]] = None
data_info: Dict = {}


@app.on_event("startup")
async def load_data():
    """Carga datos al iniciar la aplicación"""
    global io_matrix, env_extension, calculator, sector_names, data_info

    try:
        # Configuración
        data_dir = Path("data/raw")
        mip_file = "anex-MIP-2021.xlsx"
        env_file = "CAEFM-EA68aVALORADO.xlsx"
        year = 2021

        # Cargar datos
        loader = MIPDataLoader(str(data_dir))
        dataset = loader.load_complete_dataset(mip_file, env_file, year)

        # Crear objetos
        io_matrix = InputOutputMatrix(
            dataset['intermediate_consumption'],
            dataset['gross_output']
        )
        io_matrix.compute_all_matrices()

        env_extension = EnvironmentalExtension(
            io_matrix,
            dataset['environmental_pressures']
        )
        env_extension.compute_total_multipliers()

        calculator = CarbonFootprintCalculator(
            io_matrix,
            env_extension,
            ghg_indices=[0, 1, 2]
        )

        sector_names = dataset['sector_names']
        data_info = {
            'year': year,
            'n_sectors': dataset['n_sectors'],
            'n_environmental_indicators': dataset['n_environmental_indicators']
        }

        print(f"✓ Datos cargados exitosamente para el año {year}")

    except FileNotFoundError:
        print("⚠ Archivos de datos no encontrados. API funcionará sin datos.")
    except Exception as e:
        print(f"⚠ Error al cargar datos: {str(e)}")


@app.get("/", tags=["General"])
async def root():
    """Endpoint raíz"""
    return {
        "message": "Carbon Footprint Calculator API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Verifica el estado de la API"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        data_loaded=calculator is not None,
        n_sectors=data_info.get('n_sectors'),
        n_environmental_indicators=data_info.get('n_environmental_indicators')
    )


@app.get("/sectors", tags=["Info"])
async def get_sectors():
    """Obtiene lista de sectores"""
    if sector_names is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Datos no cargados"
        )

    return {
        "n_sectors": len(sector_names),
        "sectors": [
            {"index": i, "name": name}
            for i, name in enumerate(sector_names)
        ]
    }


@app.get("/sectors/{sector_index}", tags=["Info"])
async def get_sector_info(sector_index: int):
    """Obtiene información de un sector específico"""
    if calculator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Datos no cargados"
        )

    if sector_index < 0 or sector_index >= len(sector_names):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Índice de sector inválido. Debe estar entre 0 y {len(sector_names)-1}"
        )

    multipliers = io_matrix.get_sector_multipliers(sector_index)
    responsibility = calculator.calculate_sector_responsibility(sector_index)

    return {
        "sector_index": sector_index,
        "sector_name": sector_names[sector_index],
        "economic_multipliers": multipliers,
        "environmental_responsibility": responsibility
    }


@app.post("/calculate/product", tags=["Calculations"])
async def calculate_product_footprint(request: ProductFootprintRequest):
    """Calcula la huella de carbono de un producto"""
    if calculator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Datos no cargados"
        )

    try:
        result = calculator.calculate_product_footprint(
            request.sector_index,
            request.quantity,
            request.unit
        )

        # Convertir arrays a listas para JSON
        result['emissions_by_sector'] = result['emissions_by_sector'].tolist()
        result['total_production_required'] = result['total_production_required'].tolist()

        return {
            "success": True,
            "data": result,
            "sector_name": sector_names[request.sector_index]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/calculate/basket", tags=["Calculations"])
async def calculate_basket_footprint(request: BasketFootprintRequest):
    """Calcula la huella de carbono de una canasta de consumo"""
    if calculator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Datos no cargados"
        )

    if len(request.demand_vector) != len(sector_names):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El vector de demanda debe tener {len(sector_names)} elementos"
        )

    try:
        demand = np.array(request.demand_vector)
        result = calculator.calculate_basket_footprint(demand, request.basket_name)

        # Convertir arrays a listas
        result['emissions_by_sector'] = result['emissions_by_sector'].tolist()
        result['demand_contribution'] = result['demand_contribution'].tolist()
        result['total_production'] = result['total_production'].tolist()
        result['ghg_intensity'] = result['ghg_intensity'].tolist()

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/calculate/compare", tags=["Calculations"])
async def compare_scenarios(request: ScenarioComparisonRequest):
    """Compara huellas de carbono entre dos escenarios"""
    if calculator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Datos no cargados"
        )

    if len(request.baseline) != len(sector_names) or len(request.alternative) != len(sector_names):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Los vectores deben tener {len(sector_names)} elementos"
        )

    try:
        baseline = np.array(request.baseline)
        alternative = np.array(request.alternative)

        result = calculator.compare_scenarios(
            baseline,
            alternative,
            tuple(request.scenario_names)
        )

        # Convertir arrays a listas
        def convert_arrays(obj):
            if isinstance(obj, dict):
                return {k: convert_arrays(v) for k, v in obj.items()}
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, list):
                return [convert_arrays(item) for item in obj]
            else:
                return obj

        result = convert_arrays(result)

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/calculate/priorities", tags=["Calculations"])
async def get_mitigation_priorities(request: BasketFootprintRequest, n_priorities: int = 10):
    """Identifica prioridades de mitigación"""
    if calculator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Datos no cargados"
        )

    if len(request.demand_vector) != len(sector_names):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El vector de demanda debe tener {len(sector_names)} elementos"
        )

    try:
        demand = np.array(request.demand_vector)
        priorities = calculator.get_mitigation_priorities(demand, n_priorities)

        # Agregar nombres de sectores
        for priority in priorities:
            priority['sector_name'] = sector_names[priority['sector_index']]

        return {
            "success": True,
            "data": {
                "basket_name": request.basket_name,
                "n_priorities": n_priorities,
                "priorities": priorities
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/statistics/summary", tags=["Statistics"])
async def get_summary_statistics():
    """Obtiene estadísticas resumidas del sistema"""
    if calculator is None or env_extension is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Datos no cargados"
        )

    try:
        # Calcular estadísticas
        total_emissions = env_extension.D @ io_matrix.x
        ghg_emissions = np.sum(total_emissions[:3])

        return {
            "success": True,
            "data": {
                "year": data_info['year'],
                "n_sectors": data_info['n_sectors'],
                "total_ghg_emissions": float(ghg_emissions),
                "total_production": float(np.sum(io_matrix.x)),
                "average_ghg_intensity": float(ghg_emissions / np.sum(io_matrix.x)),
                "emissions_by_indicator": total_emissions.tolist()
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

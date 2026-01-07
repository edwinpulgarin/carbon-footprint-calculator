# Carbon Footprint Calculator - Huella de Carbono

[![CI Pipeline](https://github.com/username/carbon-footprint/actions/workflows/ci.yml/badge.svg)](https://github.com/username/carbon-footprint/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/username/carbon-footprint/branch/main/graph/badge.svg)](https://codecov.io/gh/username/carbon-footprint)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Sistema de cálculo de Huella de Carbono basado en la metodología de Análisis Insumo-Producto (MIP) utilizando datos de la Matriz Insumo-Producto de Colombia (DANE) y Cuentas Ambientales.

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [API REST](#-api-rest)
- [Metodología](#-metodología)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Desarrollo](#-desarrollo)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contribución](#-contribución)
- [Licencia](#-licencia)

## ✨ Características

- **Análisis Económico Completo**: Implementa matrices de Leontief y Ghosh para análisis de encadenamientos productivos
- **Extensión Ambiental**: Cálculo de intensidades ambientales directas y totales
- **Múltiples Indicadores**: Gases de Efecto Invernadero (GEI) y otros indicadores ambientales
- **API REST**: Endpoints documentados con FastAPI y Swagger UI
- **Arquitectura OOP**: Diseño orientado a objetos con principios SOLID
- **Pipeline CI/CD**: Integración y despliegue continuo con GitHub Actions
- **Containerización**: Docker para despliegue consistente
- **Documentación Completa**: Docstrings, type hints y documentación API

## 🏗️ Arquitectura

El sistema está construido con una arquitectura en capas:

```
┌─────────────────────────────────────┐
│         API Layer (FastAPI)         │
│  - REST Endpoints                   │
│  - Request/Response Validation      │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│       Service Layer                 │
│  - CarbonFootprintCalculator        │
│  - MIPDataLoader                    │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│        Model Layer                  │
│  - InputOutputMatrix                │
│  - EnvironmentalExtension           │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│         Data Layer                  │
│  - Excel Files (MIP + Env Accounts) │
└─────────────────────────────────────┘
```

## 🚀 Instalación

### Prerequisitos

- Python 3.9 o superior
- pip
- Git

### Instalación Local

```bash
# Clonar el repositorio
git clone https://github.com/username/carbon-footprint.git
cd carbon-footprint

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Colocar archivos de datos en data/raw/
# - anex-MIP-2021.xlsx
# - CAEFM-EA68aVALORADO.xlsx
```

### Instalación con Docker

```bash
# Construir imagen
docker build -t carbon-footprint-api .

# Ejecutar contenedor
docker run -p 8000:8000 carbon-footprint-api
```

## 💻 Uso

### Uso Programático

```python
from src.models.input_output_matrix import InputOutputMatrix
from src.models.environmental_extension import EnvironmentalExtension
from src.services.data_loader import MIPDataLoader
from src.services.carbon_calculator import CarbonFootprintCalculator

# Cargar datos
loader = MIPDataLoader('data/raw')
dataset = loader.load_complete_dataset(
    'anex-MIP-2021.xlsx',
    'CAEFM-EA68aVALORADO.xlsx',
    2021
)

# Crear matriz IO
io_matrix = InputOutputMatrix(
    dataset['intermediate_consumption'],
    dataset['gross_output']
)
io_matrix.compute_all_matrices()

# Crear extensión ambiental
env_extension = EnvironmentalExtension(
    io_matrix,
    dataset['environmental_pressures']
)

# Calculadora de huella
calculator = CarbonFootprintCalculator(
    io_matrix,
    env_extension,
    ghg_indices=[0, 1, 2]
)

# Calcular huella de un producto
footprint = calculator.calculate_product_footprint(
    sector_idx=15,
    quantity=1000000
)

print(f"Huella total: {footprint['total_footprint']} ton CO2eq")
```

### Ejecutar API

```bash
# Desarrollo
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Producción
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Acceder a la documentación interactiva:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🌐 API REST

### Endpoints Principales

#### GET /health
Verifica el estado de la API
```bash
curl http://localhost:8000/health
```

#### GET /sectors
Lista todos los sectores económicos
```bash
curl http://localhost:8000/sectors
```

#### POST /calculate/product
Calcula la huella de carbono de un producto
```bash
curl -X POST http://localhost:8000/calculate/product \
  -H "Content-Type: application/json" \
  -d '{
    "sector_index": 15,
    "quantity": 1000000,
    "unit": "monetary"
  }'
```

#### POST /calculate/basket
Calcula la huella de una canasta de consumo
```bash
curl -X POST http://localhost:8000/calculate/basket \
  -H "Content-Type: application/json" \
  -d '{
    "demand_vector": [100000, 200000, ...],
    "basket_name": "Canasta familiar"
  }'
```

#### POST /calculate/compare
Compara dos escenarios de consumo
```bash
curl -X POST http://localhost:8000/calculate/compare \
  -H "Content-Type: application/json" \
  -d '{
    "baseline": [100000, ...],
    "alternative": [80000, ...],
    "scenario_names": ["Base", "Alternativa"]
  }'
```

#### POST /calculate/priorities
Identifica prioridades de mitigación
```bash
curl -X POST http://localhost:8000/calculate/priorities?n_priorities=10 \
  -H "Content-Type: application/json" \
  -d '{
    "demand_vector": [100000, ...],
    "basket_name": "Nacional"
  }'
```

## 📊 Metodología

### Análisis Insumo-Producto

El sistema implementa la metodología estándar de Análisis Insumo-Producto según Miller & Blair (2009):

1. **Matriz de Coeficientes Técnicos**: `A = Z × X̂⁻¹`
2. **Inversa de Leontief (Backward Linkages)**: `L = (I - A)⁻¹`
3. **Inversa de Ghosh (Forward Linkages)**: `G = (I - B)⁻¹`

### Extensión Ambiental

Siguiendo las guías de Eurostat para cuentas satélite ambientales:

1. **Intensidad Directa**: `D = D₁ × X̂⁻¹`
2. **Multiplicadores Totales**: `Dₐ = D × L`
3. **Encadenamientos Ambientales**: Índices BL y FL

### Huella de Carbono

**Enfoque Consumidor**:
```
Huella = Σ(intensidad_GEI_sector × demanda_final_sector)
```

**Enfoque Productor**:
```
Emisiones = Σ(coeficiente_emisión_sector × producción_sector)
```

## 📁 Estructura del Proyecto

```
carbon-footprint/
├── .github/
│   └── workflows/
│       ├── ci.yml                 # Pipeline CI
│       └── cd.yml                 # Pipeline CD
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py               # FastAPI application
│   ├── models/
│   │   ├── __init__.py
│   │   ├── input_output_matrix.py      # Modelo MIP
│   │   └── environmental_extension.py  # Extensión ambiental
│   └── services/
│       ├── __init__.py
│       ├── data_loader.py              # Carga de datos
│       └── carbon_calculator.py        # Calculadora principal
├── tests/
│   ├── __init__.py
│   ├── test_io_matrix.py
│   ├── test_environmental.py
│   └── test_api.py
├── data/
│   ├── raw/                      # Datos originales (no versionados)
│   └── processed/                # Datos procesados
├── docs/
│   ├── api_guide.md
│   ├── methodology.md
│   └── examples/
├── config/
│   ├── settings.py
│   └── logging.conf
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── setup.py
├── pytest.ini
├── README.md
└── LICENSE
```

## 🛠️ Desarrollo

### Setup Entorno de Desarrollo

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Instalar pre-commit hooks
pre-commit install

# Configurar variables de entorno
cp .env.example .env
```

### Estándares de Código

- **Formato**: Black (line length: 100)
- **Linting**: Flake8
- **Type Checking**: MyPy
- **Import Sorting**: isort
- **Docstrings**: Google style

```bash
# Formatear código
black src/

# Ordenar imports
isort src/

# Verificar tipos
mypy src/

# Linting
flake8 src/
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=src --cov-report=html

# Tests específicos
pytest tests/test_io_matrix.py -v

# Tests de integración
pytest tests/integration/ -v
```

### Estructura de Tests

```python
# tests/test_io_matrix.py
import pytest
import numpy as np
from src.models.input_output_matrix import InputOutputMatrix

def test_leontief_inverse():
    Z = np.array([[10, 20], [30, 40]])
    x = np.array([100, 200])

    io_matrix = InputOutputMatrix(Z, x)
    L = io_matrix.compute_leontief_inverse()

    assert L.shape == (2, 2)
    assert np.all(np.diag(L) >= 1)  # Diagonal >= 1
```

## 🚢 Deployment

### Variables de Entorno

```bash
# .env
API_HOST=0.0.0.0
API_PORT=8000
DATA_DIR=data/raw
LOG_LEVEL=INFO
WORKERS=4
```

### Docker Compose

```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

### Deployment en Cloud

#### AWS ECS
```bash
# Build y push a ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
docker build -t carbon-footprint-api .
docker tag carbon-footprint-api:latest ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/carbon-footprint-api:latest
docker push ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/carbon-footprint-api:latest
```

## 📈 Monitoreo

### Métricas Disponibles

- Tiempo de respuesta de endpoints
- Tasa de errores
- Uso de memoria
- Número de requests por segundo

### Logs

```python
# Configuración en config/logging.conf
import logging

logger = logging.getLogger(__name__)
logger.info("Cálculo completado")
```

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Guidelines

- Escribe tests para código nuevo
- Mantén cobertura > 80%
- Sigue los estándares de código
- Actualiza la documentación

## 📚 Referencias

- Miller, R. E., & Blair, P. D. (2009). *Input-Output Analysis: Foundations and Extensions*. Cambridge University Press.
- Eurostat (2008). *Eurostat Manual of Supply, Use and Input-Output Tables*.
- DANE Colombia - Matrices Insumo-Producto
- DANE Colombia - Cuentas Ambientales

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo [LICENSE](LICENSE) para más detalles.

## 👥 Autores

- **Equipo de Desarrollo** - *Trabajo Inicial* - [GitHub](https://github.com/username)

## 🙏 Agradecimientos

- DANE Colombia por los datos de MIP y Cuentas Ambientales
- Comunidad de Python científico (NumPy, Pandas)
- FastAPI por el excelente framework

---

**Nota**: Este proyecto es para fines educativos y de investigación. Para uso en producción, verificar y validar todos los cálculos con expertos en análisis ambiental.

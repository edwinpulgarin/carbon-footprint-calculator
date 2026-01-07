# Guía de Inicio Rápido

## 📦 Preparación de Datos

1. Coloca los archivos de datos en el directorio `data/raw/`:
   - `anex-MIP-2021.xlsx` (Matriz Insumo-Producto del DANE)
   - `CAEFM-EA68aVALORADO.xlsx` (Cuentas Ambientales del DANE)

```bash
mkdir -p data/raw
# Copiar archivos Excel al directorio data/raw/
```

## 🚀 Instalación y Ejecución

### Opción 1: Instalación Local

```bash
# 1. Clonar repositorio
git clone <repository-url>
cd Entregable_CEP

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar API
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Opción 2: Docker

```bash
# 1. Construir y ejecutar con Docker Compose
docker-compose up -d

# 2. Ver logs
docker-compose logs -f

# 3. Detener
docker-compose down
```

## 🌐 Acceder a la API

Una vez ejecutada, accede a:

- **Documentación Interactiva (Swagger)**: http://localhost:8000/docs
- **Documentación Alternativa (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📝 Ejemplos de Uso

### 1. Verificar Estado de la API

```bash
curl http://localhost:8000/health
```

Respuesta:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "data_loaded": true,
  "n_sectors": 68,
  "n_environmental_indicators": 7
}
```

### 2. Listar Sectores Disponibles

```bash
curl http://localhost:8000/sectors
```

### 3. Calcular Huella de un Producto

```bash
curl -X POST http://localhost:8000/calculate/product \
  -H "Content-Type: application/json" \
  -d '{
    "sector_index": 15,
    "quantity": 1000000,
    "unit": "monetary"
  }'
```

Respuesta:
```json
{
  "success": true,
  "data": {
    "sector_index": 15,
    "quantity": 1000000,
    "total_footprint": 1234.56,
    "direct_emissions": 456.78,
    "indirect_emissions": 777.78,
    "direct_intensity": 0.0004567
  },
  "sector_name": "Manufactura de alimentos"
}
```

### 4. Calcular Huella de Canasta

```bash
curl -X POST http://localhost:8000/calculate/basket \
  -H "Content-Type: application/json" \
  -d '{
    "demand_vector": [100000, 200000, 150000, ...],
    "basket_name": "Canasta familiar mensual"
  }'
```

### 5. Comparar Escenarios

```bash
curl -X POST http://localhost:8000/calculate/compare \
  -H "Content-Type: application/json" \
  -d '{
    "baseline": [100000, 200000, 150000, ...],
    "alternative": [80000, 180000, 140000, ...],
    "scenario_names": ["Escenario Base 2021", "Escenario Optimizado"]
  }'
```

### 6. Identificar Prioridades de Mitigación

```bash
curl -X POST "http://localhost:8000/calculate/priorities?n_priorities=10" \
  -H "Content-Type: application/json" \
  -d '{
    "demand_vector": [100000, 200000, 150000, ...],
    "basket_name": "Consumo Nacional"
  }'
```

## 🐍 Uso Programático en Python

```python
import requests
import json

# URL base de la API
BASE_URL = "http://localhost:8000"

# 1. Verificar estado
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# 2. Calcular huella de producto
product_data = {
    "sector_index": 15,
    "quantity": 1000000,
    "unit": "monetary"
}

response = requests.post(
    f"{BASE_URL}/calculate/product",
    json=product_data
)

result = response.json()
print(f"Huella total: {result['data']['total_footprint']} ton CO2eq")

# 3. Obtener sectores
response = requests.get(f"{BASE_URL}/sectors")
sectors = response.json()

for sector in sectors['sectors'][:5]:
    print(f"{sector['index']}: {sector['name']}")
```

## 🧪 Ejecutar Tests

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=src --cov-report=html

# Tests específicos
pytest tests/test_io_matrix.py -v

# Ver reporte de cobertura
# Abrir htmlcov/index.html en el navegador
```

## 📊 Estructura de Datos

### Vector de Demanda Final

El vector de demanda debe tener **68 elementos** (uno por sector):

```python
demand_vector = [
    1000000,  # Sector 0: Agricultura
    500000,   # Sector 1: Ganadería
    750000,   # Sector 2: Pesca
    # ... (65 sectores más)
]
```

### Índices de Sectores

Los sectores están indexados de 0 a 67. Consulta `/sectors` para ver la lista completa.

### Unidades

- **Producción/Demanda**: Millones de pesos colombianos
- **Emisiones**: Toneladas de CO2 equivalente
- **Intensidad**: ton CO2eq / millón de pesos

## 🔧 Configuración

### Variables de Entorno

Crea un archivo `.env` basado en `.env.example`:

```bash
cp .env.example .env
```

Edita `.env`:

```bash
API_HOST=0.0.0.0
API_PORT=8000
DATA_DIR=data/raw
LOG_LEVEL=INFO
```

## 🐛 Solución de Problemas

### Error: "Datos no cargados"

**Causa**: Los archivos Excel no están en `data/raw/`

**Solución**:
```bash
# Verificar archivos
ls data/raw/
# Debe mostrar: anex-MIP-2021.xlsx  CAEFM-EA68aVALORADO.xlsx
```

### Error: "El vector de demanda debe tener 68 elementos"

**Causa**: Vector de demanda con dimensión incorrecta

**Solución**: Asegúrate de que el vector tenga exactamente 68 elementos

### Error de Importación

**Causa**: Dependencias no instaladas

**Solución**:
```bash
pip install -r requirements.txt
```

## 📚 Recursos Adicionales

- [README.md](README.md) - Documentación completa
- [API Documentation](http://localhost:8000/docs) - Documentación interactiva
- [Metodología.pdf](Metodología.pdf) - Fundamentos teóricos
- [Script_R_Documentado.R](Script_R_Documentado.R) - Código R original

## 💡 Tips

1. **Explorar la API**: Usa la interfaz Swagger en `/docs` para explorar todos los endpoints
2. **Validación**: La API valida automáticamente los datos de entrada
3. **Logs**: Revisa los logs en la consola para debugging
4. **Performance**: Los cálculos se cachean para mejorar rendimiento
5. **Tests**: Ejecuta tests antes de modificar código

## 🔄 Workflow Típico

```bash
# 1. Preparar entorno
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 2. Colocar datos
# Copiar archivos Excel a data/raw/

# 3. Ejecutar API
uvicorn src.api.main:app --reload

# 4. Probar endpoints
# Abrir http://localhost:8000/docs

# 5. Ejecutar tests (opcional)
pytest

# 6. Desarrollar/modificar código
# Usar pre-commit hooks: pre-commit install
```

## 📞 Soporte

Para preguntas o problemas:
- Revisar issues en GitHub
- Consultar documentación en `/docs`
- Verificar logs de la aplicación

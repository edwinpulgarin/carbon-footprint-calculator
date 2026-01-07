# Carbon Footprint Calculator - Huella de Carbono

[![CI Pipeline](https://github.com/edwinpulgarin/carbon-footprint-calculator/actions/workflows/ci.yml/badge.svg)](https://github.com/edwinpulgarin/carbon-footprint-calculator/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Validation](https://img.shields.io/badge/validation-100%25-brightgreen)](REPORTE_VALIDACION.md)

Sistema profesional de cálculo de Huella de Carbono basado en la metodología de **Análisis Insumo-Producto (MIP)** utilizando datos oficiales de la Matriz Insumo-Producto de Colombia (DANE) y Cuentas Ambientales.

**Sistema Validado**: 100% de precisión con datos reales 2017-2021 ([Ver Reporte](REPORTE_VALIDACION.md))

**Deploy Rápido**: [QUICK_DEPLOY.md](QUICK_DEPLOY.md) - En línea en 10 minutos

---

## Contenidos

- [Características](#características) | [Metodología](#metodología-científica) | [Instalación](#instalación-rápida) | [API REST](#api-rest) | [Deploy](#despliegue) | [Documentación Completa](#referencias-principales)

---

## Características

- **68 Sectores** económicos de Colombia
- **7 Indicadores** ambientales (CO₂, CH₄, N₂O + otros)
- **Matrices Leontief y Ghosh** (encadenamientos productivos)
- **Multiplicadores ambientales** directos + indirectos
- **API REST** con 8 endpoints documentados
- **Validación 100%** con datos reales 2017-2021
- **Dashboard web** interactivo incluido

---

## Metodología Científica

### **Fundamento Teórico**

Sistema basado en **Análisis Insumo-Producto** (Leontief, 1973 - Premio Nobel) con extensión ambiental según guías de Eurostat y SEEA.

### **1. Matriz Insumo-Producto**

#### **Estructura Básica**
```
        Sectores (j)
         ┌───────────┐
Sectores │ Z₁₁ ... Z₁ₙ │ F₁  │ x₁
  (i)    │ ... ... ... │ ... │ ...
         │ Zₙ₁ ... Zₙₙ │ Fₙ  │ xₙ
         └─────────────┴─────┴────
          Consumo       Demanda  Producción
          Intermedio    Final    Bruta
```

- **Zᵢⱼ**: Uso del producto i por sector j
- **Fᵢ**: Demanda final del producto i
- **xᵢ**: Producción total del producto i

#### **Coeficientes Técnicos (A)**
```
A = Z × X̂⁻¹
```
Donde `X̂ = diag(x)`

**Interpretación**: `aᵢⱼ` = unidades de i necesarias para producir 1 unidad de j

#### **Inversa de Leontief (L)** - Backward Linkages
```
L = (I - A)⁻¹
x = L × F
```

**Interpretación**: `lᵢⱼ` = producción total de i (directa + indirecta) para satisfacer 1 unidad de demanda final de j

**Propiedad validada**: `L(I - A) = I`

#### **Inversa de Ghosh (G)** - Forward Linkages
```
B = X̂⁻¹ × Z
G = (I - B)⁻¹
```

**Interpretación**: Cómo la producción de i se distribuye hacia j en la cadena de suministro

### **2. Extensión Ambiental**

#### **Intensidad Directa (D)**
```
D = D₁ × X̂⁻¹
```

Donde **D₁** es la matriz de presiones ambientales absolutas (ton CO₂, m³ agua, etc.)

**Unidades**: ton CO₂eq / millón COP

#### **Multiplicadores Totales (Dₐ)**
```
Dₐ = D × L
```

**Interpretación**: Emisiones totales (directas + indirectas) por unidad de demanda final

**Propiedad**: `Dₐ ≥ D` (siempre)

### **3. Encadenamientos Ambientales**

#### **Backward Linkage (BL)**
```
Lₑₙᵥ = α × L
BLⱼ = (Σᵢ Lₑₙᵥ,ᵢⱼ) / promedio
```

- **BL > 1**: Sector estimula muchas emisiones en proveedores
- **BL < 1**: Sector con bajo impacto hacia atrás

#### **Forward Linkage (FL)**
```
Gₑₙᵥ = G × αᵀ
FLᵢ = (Σⱼ Gₑₙᵥ,ᵢⱼ) / promedio
```

- **FL > 1**: Sector distribuye emisiones ampliamente
- **FL < 1**: Distribución concentrada

#### **Sectores Clave**
```
BL > 1 Y FL > 1 → SECTOR CLAVE (prioritario para mitigación)
```

### **4. Cálculo de Huella de Carbono**

#### **Huella de Producto**
```
CFⱼ = Σₖ∈GEI (Dₐ)ₖⱼ × yⱼ

Donde:
CF_direct = Σₖ∈GEI dₖⱼ × yⱼ
CF_indirect = CFⱼ - CF_direct
```

#### **Huella de Canasta**
```
CF_total = Σₖ∈GEI Σⱼ (Dₐ)ₖⱼ × yⱼ
```

### **5. Validación Matemática**

Sistema valida automáticamente:

- **L(I-A) = I** (error < 10⁻⁴)
- **Diagonal L ≥ 1**
- **Σᵢ aᵢⱼ < 1** (productividad)
- **Dₐ ≥ D** (multiplicadores)
- **D×x = emisiones totales** (reconstrucción)

**Resultado**: 100% validado en datos 2017-2021

---

## Instalación Rápida

```bash
# 1. Clonar
git clone https://github.com/edwinpulgarin/carbon-footprint-calculator.git
cd carbon-footprint-calculator

# 2. Instalar
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 3. Ejecutar
uvicorn src.api.main:app --reload

# 4. Abrir: http://localhost:8000/docs
```

Los datos (Excel) ya están incluidos en `data/raw/`

---

## API REST

### Endpoints Principales

```bash
# Health check
GET  /health

# Sectores
GET  /sectors
GET  /sectors/{id}

# Cálculos
POST /calculate/product     # Huella de producto
POST /calculate/basket      # Huella de canasta
POST /calculate/compare     # Comparar escenarios
POST /calculate/priorities  # Prioridades mitigación

# Estadísticas
GET  /statistics/summary
```

### Ejemplo de Uso

```bash
curl -X POST http://localhost:8000/calculate/product \
  -H "Content-Type: application/json" \
  -d '{"sector_index": 15, "quantity": 1000000}'
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "total_footprint": 1649661.16,
    "direct_emissions": 1595497.90,
    "indirect_emissions": 54163.26
  }
}
```

**Documentación interactiva**: `/docs` (Swagger UI)

---

## Despliegue

### Opción 1: Railway (5 min) - RECOMENDADO

```bash
1. https://railway.app → Login GitHub
2. New Project → Deploy from GitHub
3. Seleccionar: edwinpulgarin/carbon-footprint-calculator
4. Esperar 2-3 min
5. Generate Domain
```

**Gratis** hasta $5/mes

### Opción 2: Otros

- **Render**: Ver [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Google Cloud**: Ver [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Dashboard Web**: Ver [frontend/index.html](frontend/index.html)

**Guía completa**: [QUICK_DEPLOY.md](QUICK_DEPLOY.md)

---

## Uso Programático

### Python
```python
from src.services.carbon_calculator import CarbonFootprintCalculator

# ... (ver ejemplos completos en docs/)

footprint = calculator.calculate_product_footprint(
    sector_idx=15,
    quantity=1_000_000
)
```

### JavaScript
```javascript
const response = await fetch('http://localhost:8000/calculate/product', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({sector_index: 15, quantity: 1000000})
});
```

### R
```r
library(httr)
POST("http://localhost:8000/calculate/product",
     body = list(sector_index = 15, quantity = 1000000),
     encode = "json")
```

---

## Resultados Validados

### Colombia 2017-2021

| Métrica | 2017 | 2019 | 2021 | Tendencia |
|---------|------|------|------|-----------|
| **Producción** (M COP) | 1.6M | 1.9M | 2.1M | +32% |
| **Emisiones GEI** (ton) | 123k | 126k | 117k | -5% |
| **Intensidad** (ton/M) | 76.2 | 67.8 | 54.8 | -28% |

**Conclusión**: Desacoplamiento economía-emisiones

### Sectores Clave Identificados

1. **Coquización y refinación** (BL≈24, FL≈21)
2. **Elaboración de azúcar** (BL≈15, FL≈16)
3. **Extracción de carbón** (BL≈2.5, FL≈3.2)

[Ver Reporte Completo](REPORTE_VALIDACION.md)

---

## Estructura del Proyecto

```
carbon-footprint-calculator/
├── src/                  # Código fuente (~1,500 líneas)
│   ├── api/             # FastAPI (8 endpoints)
│   ├── models/          # Modelos OOP (MIP, Env)
│   └── services/        # Servicios (Calculator, Loader)
├── data/raw/            # Datos DANE (Excel incluidos)
├── frontend/            # Dashboard web
├── tests/               # Tests unitarios
├── .github/workflows/   # CI/CD pipelines
└── docs/                # Documentación
```

---

## Referencias Principales

1. **Miller & Blair (2009)**. *Input-Output Analysis: Foundations and Extensions*. Cambridge Univ. Press.
2. **Eurostat (2008)**. *Manual of Supply, Use and Input-Output Tables*.
3. **DANE (2023)**. *Matriz Insumo-Producto de Colombia*.
4. **Wiedmann & Minx (2008)**. A definition of 'carbon footprint'. *Ecol. Econ. Research Trends*.

---

## Contribución

```bash
git checkout -b feature/nueva-funcionalidad
# ... hacer cambios
pytest  # tests pasan
git commit -m "feat: add funcionalidad"
git push origin feature/nueva-funcionalidad
# → Pull Request en GitHub
```

---

## Licencia

MIT License - Ver [LICENSE](LICENSE)

---

## Autor

**Edwin Pulgarin** - [GitHub](https://github.com/edwinpulgarin)

---

## Soporte

- **Issues**: https://github.com/edwinpulgarin/carbon-footprint-calculator/issues
- **Docs**: Ver archivos `.md` en el repositorio
- **Deploy**: [QUICK_DEPLOY.md](QUICK_DEPLOY.md)

---

**Contribuyendo a un futuro sostenible mediante análisis económico-ambiental riguroso.**

---

## Documentación Adicional

- [QUICK_DEPLOY.md](QUICK_DEPLOY.md) - Deploy en 10 minutos
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Guía completa deployment
- [REPORTE_VALIDACION.md](REPORTE_VALIDACION.md) - Validación 100%
- [QUICK_START.md](QUICK_START.md) - Guía de inicio
- [GITHUB_SETUP.md](GITHUB_SETUP.md) - Configuración GitHub

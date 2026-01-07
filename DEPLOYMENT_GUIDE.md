# 🚀 Guía de Despliegue en la Nube

Esta guía te ayudará a desplegar el sistema de Huella de Carbono en la nube para que tu equipo pueda acceder a todo en línea.

---

## 📋 Opciones de Despliegue Recomendadas

### **Opción 1: Railway (RECOMENDADO - MÁS FÁCIL)** ⭐

**Ventajas:**
- ✅ Despliegue en 5 minutos
- ✅ GRATIS hasta $5/mes de uso
- ✅ SSL automático (HTTPS)
- ✅ Deploy desde GitHub automático
- ✅ Dominio público incluido

**Pasos:**

1. **Crear cuenta en Railway**
   ```
   https://railway.app
   - Sign up with GitHub
   ```

2. **Nuevo Proyecto**
   ```
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Autorizar Railway en GitHub
   - Seleccionar repositorio: carbon-footprint
   ```

3. **Configurar Variables**
   ```
   En Railway Dashboard:
   - Settings → Variables
   - Add: PORT=8000
   - Add: DATA_DIR=data/raw
   ```

4. **Deploy Automático**
   ```
   Railway detecta el Dockerfile automáticamente
   Deploy ocurre automáticamente
   ```

5. **Obtener URL**
   ```
   Settings → Domains → Generate Domain
   URL: https://tu-proyecto.up.railway.app
   ```

**Acceso a la API:**
```
https://tu-proyecto.up.railway.app/docs
https://tu-proyecto.up.railway.app/health
```

---

### **Opción 2: Render** 🔷

**Ventajas:**
- ✅ Plan gratuito disponible
- ✅ Deploy automático desde GitHub
- ✅ SSL incluido
- ✅ Buena documentación

**Pasos:**

1. **Crear cuenta**
   ```
   https://render.com
   - Sign up with GitHub
   ```

2. **Nuevo Web Service**
   ```
   Dashboard → New → Web Service
   - Connect GitHub repository
   - Seleccionar: carbon-footprint
   ```

3. **Configuración**
   ```
   Name: carbon-footprint-api
   Environment: Docker
   Plan: Free
   ```

4. **Variables de Entorno**
   ```
   Environment → Add Environment Variable:
   - PORT=8000
   - DATA_DIR=data/raw
   ```

5. **Deploy**
   ```
   Click "Create Web Service"
   URL: https://carbon-footprint-api.onrender.com
   ```

**Nota**: El plan gratuito se "duerme" después de 15 min de inactividad.

---

### **Opción 3: Google Cloud Run** ☁️

**Ventajas:**
- ✅ Escalabilidad automática
- ✅ Pago por uso (muy económico)
- ✅ Integración con GCP
- ✅ Alta disponibilidad

**Pasos:**

1. **Instalar Google Cloud SDK**
   ```bash
   # Windows
   https://cloud.google.com/sdk/docs/install

   # Linux/Mac
   curl https://sdk.cloud.google.com | bash
   ```

2. **Login y Configuración**
   ```bash
   gcloud auth login
   gcloud config set project TU-PROYECTO-ID
   ```

3. **Build y Push de Imagen**
   ```bash
   # Build imagen
   gcloud builds submit --tag gcr.io/TU-PROYECTO/carbon-api

   # Deploy
   gcloud run deploy carbon-api \
     --image gcr.io/TU-PROYECTO/carbon-api \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

4. **Obtener URL**
   ```
   URL proporcionada automáticamente:
   https://carbon-api-xxxxx-uc.a.run.app
   ```

---

### **Opción 4: AWS (Amazon)** 🟠

**Usando AWS App Runner:**

1. **AWS Console**
   ```
   https://console.aws.amazon.com
   → App Runner → Create Service
   ```

2. **Source**
   ```
   - Source: Container registry
   - Provider: ECR
   - O conectar con GitHub
   ```

3. **Configuración**
   ```
   Service name: carbon-footprint-api
   Port: 8000
   CPU: 1 vCPU
   Memory: 2 GB
   ```

4. **Deploy**
   ```
   URL: https://xxxxx.us-east-1.awsapprunner.com
   ```

---

## 🌐 Configurar Acceso Web a Resultados

### **Opción A: API + Frontend Simple**

Voy a crear un frontend web simple que consuma la API:

```html
<!-- Archivo: frontend/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Carbon Footprint Calculator</title>
    <style>
        body { font-family: Arial; max-width: 1200px; margin: 0 auto; padding: 20px; }
        .result { background: #f0f0f0; padding: 15px; margin: 10px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>🌍 Carbon Footprint Calculator</h1>

    <div id="health-status"></div>
    <div id="sectors-list"></div>
    <div id="results"></div>

    <script>
        const API_URL = 'https://tu-api.railway.app'; // Cambiar por tu URL

        // Verificar estado
        fetch(`${API_URL}/health`)
            .then(r => r.json())
            .then(data => {
                document.getElementById('health-status').innerHTML =
                    `<div class="result">Status: ${data.status} ✅</div>`;
            });

        // Cargar sectores
        fetch(`${API_URL}/sectors`)
            .then(r => r.json())
            .then(data => {
                const html = data.sectors.slice(0, 10).map(s =>
                    `<li>${s.index}: ${s.name}</li>`
                ).join('');
                document.getElementById('sectors-list').innerHTML =
                    `<div class="result"><h3>Sectores:</h3><ul>${html}</ul></div>`;
            });
    </script>
</body>
</html>
```

**Desplegar frontend:**
1. **GitHub Pages** (gratis)
   ```bash
   # Crear carpeta frontend
   mkdir frontend
   # Copiar index.html
   # Push a GitHub
   # Settings → Pages → Deploy from main/frontend
   ```

2. **Netlify** (gratis)
   ```
   https://netlify.com
   - Drag & drop carpeta frontend
   - URL: https://carbon-footprint.netlify.app
   ```

---

### **Opción B: Dashboard con Streamlit** 📊

Crear dashboard interactivo:

```python
# dashboard.py
import streamlit as st
import requests

st.title("🌍 Carbon Footprint Dashboard")

API_URL = "https://tu-api.railway.app"

# Health check
health = requests.get(f"{API_URL}/health").json()
st.success(f"API Status: {health['status']}")

# Sectores
sectors = requests.get(f"{API_URL}/sectors").json()
st.write(f"Total sectores: {sectors['n_sectors']}")

# Calcular huella
st.header("Calcular Huella de Producto")
sector_idx = st.number_input("Índice de sector", 0, 67, 15)
quantity = st.number_input("Cantidad (COP)", 100000, 10000000, 1000000)

if st.button("Calcular"):
    result = requests.post(
        f"{API_URL}/calculate/product",
        json={"sector_index": sector_idx, "quantity": quantity}
    ).json()

    st.metric("Huella Total", f"{result['data']['total_footprint']:.2f} ton CO2eq")
    st.metric("Emisiones Directas", f"{result['data']['direct_emissions']:.2f}")
    st.metric("Emisiones Indirectas", f"{result['data']['indirect_emissions']:.2f}")
```

**Desplegar en Streamlit Cloud:**
```
1. https://streamlit.io/cloud
2. New app → From GitHub
3. Repositorio: carbon-footprint
4. Main file: dashboard.py
5. Deploy
```

---

## 📊 Opciones para Compartir Resultados

### **1. Documentación en GitHub Pages**

```bash
# Activar GitHub Pages
# GitHub → Settings → Pages
# Source: main branch / docs folder

# Tu documentación estará en:
# https://tu-usuario.github.io/carbon-footprint/
```

Estructura recomendada:
```
docs/
├── index.html           # Página principal
├── api-guide.html       # Guía de API
├── results/
│   ├── 2017.html       # Resultados 2017
│   ├── 2019.html       # Resultados 2019
│   └── 2021.html       # Resultados 2021
└── validation.html      # Reporte de validación
```

### **2. Notion/Confluence**

Exportar toda la documentación a:
- **Notion**: Workspace colaborativo
- **Confluence**: Documentación empresarial

### **3. README en GitHub**

Tu README.md ya es público y accesible en:
```
https://github.com/tu-usuario/carbon-footprint
```

---

## 🔐 Seguridad y Acceso

### **Autenticación Básica**

Si necesitas controlar acceso:

```python
# En main.py
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

@app.get("/protected")
def protected_route(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != "admin" or credentials.password != "secret":
        raise HTTPException(status_code=401)
    return {"message": "Acceso permitido"}
```

### **API Keys**

```python
# Variables de entorno
API_KEY = os.getenv("API_KEY", "default-key")

@app.get("/api-key-protected")
def protected(api_key: str = Header(None)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403)
    return {"message": "Autorizado"}
```

---

## 💰 Costos Estimados

| Plataforma | Plan Gratuito | Plan Pagado |
|------------|---------------|-------------|
| **Railway** | $5/mes incluidos | $5+ por uso adicional |
| **Render** | Ilimitado (con sleep) | $7/mes sin sleep |
| **Google Cloud Run** | 2M requests/mes | ~$0.10 por millón |
| **AWS App Runner** | No gratuito | $0.064/vCPU-hora |
| **Heroku** | ❌ Ya no gratuito | $7/mes |

**Recomendación**: Railway para empezar (más fácil y generoso).

---

## 📱 Acceso Móvil

Con cualquier opción, tu equipo puede acceder desde:
- 💻 Navegador web (cualquier dispositivo)
- 📱 Apps móviles (con la API)
- 🔗 Links directos a resultados
- 📊 Dashboards interactivos

---

## 🚀 Despliegue Rápido (5 minutos)

**Opción más rápida - Railway:**

```bash
# 1. Instalar Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Deploy
cd Entregable_CEP
railway init
railway up

# 4. Ver URL
railway domain
```

**¡Listo!** Tu API estará en línea en: `https://xxxxx.up.railway.app`

---

## 📧 Compartir con el Equipo

Una vez desplegado, comparte:

```
🌍 Carbon Footprint Calculator

📖 Documentación: https://tu-api.railway.app/docs
❤️ Health Check: https://tu-api.railway.app/health
📊 Dashboard: https://tu-dashboard.streamlit.app
📁 GitHub: https://github.com/tu-usuario/carbon-footprint
📝 Reportes: https://tu-usuario.github.io/carbon-footprint/
```

---

## 🔄 Actualización Automática

Con GitHub Actions (ya configurado):
- ✅ Cada push a main ejecuta tests
- ✅ Si tests pasan, deploy automático
- ✅ Tu equipo siempre ve la última versión

---

## 🆘 Soporte

- Railway: https://railway.app/help
- Render: https://render.com/docs
- Google Cloud: https://cloud.google.com/support
- GitHub Pages: https://docs.github.com/pages

---

**¿Cuál prefieres?** Te recomiendo **Railway** por facilidad y generosidad del plan gratuito.

# 🚀 Despliegue Rápido en 10 Minutos

## ✅ **Opción Más Fácil: Railway** (RECOMENDADO)

### **Paso 1: Subir a GitHub** (2 min)

```bash
# Si no has conectado con GitHub aún:

# 1. Crear repositorio en GitHub
#    https://github.com/new
#    Nombre: carbon-footprint-calculator

# 2. Conectar y subir
git remote add origin https://github.com/TU-USUARIO/carbon-footprint-calculator.git
git branch -M main
git push -u origin main
```

### **Paso 2: Deploy en Railway** (3 min)

1. **Ir a Railway**
   ```
   https://railway.app
   ```

2. **Login con GitHub**
   - Click "Login with GitHub"
   - Autorizar Railway

3. **Nuevo Proyecto**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Buscar: `carbon-footprint-calculator`
   - Click en tu repositorio

4. **Configurar (automático)**
   - Railway detecta el Dockerfile
   - Deploy comienza automáticamente
   - Esperar 2-3 minutos

5. **Obtener URL**
   - Click en tu proyecto
   - Pestaña "Settings"
   - Section "Domains"
   - Click "Generate Domain"
   - **Copiar URL**: `https://carbon-footprint-xxxxx.up.railway.app`

### **Paso 3: Verificar** (1 min)

Abrir en navegador:
```
https://tu-url.up.railway.app/docs
https://tu-url.up.railway.app/health
```

¡Listo! Tu API está en línea 🎉

---

## 🌐 **Desplegar Frontend (Dashboard Web)**

### **Opción A: Netlify** (2 min)

1. **Ir a Netlify**
   ```
   https://app.netlify.com
   ```

2. **Login con GitHub**

3. **New Site from Git**
   - Click "Add new site" → "Import from Git"
   - Seleccionar repositorio
   - Branch: `main`
   - Publish directory: `frontend`
   - Click "Deploy"

4. **Configurar API URL**
   - Editar `frontend/index.html`
   - Línea 244: cambiar `const API_URL = ...`
   - Por tu URL de Railway

5. **URL del Dashboard**
   ```
   https://carbon-footprint.netlify.app
   ```

### **Opción B: GitHub Pages** (3 min)

```bash
# 1. Crear rama gh-pages
git checkout -b gh-pages

# 2. Mantener solo frontend
git rm -r --cached .
git add frontend/* README.md REPORTE_VALIDACION.md
git commit -m "GitHub Pages"

# 3. Push
git push origin gh-pages

# 4. Activar en GitHub
# Settings → Pages → Source: gh-pages → /root → Save
```

URL: `https://tu-usuario.github.io/carbon-footprint-calculator/frontend/`

---

## 📱 **Compartir con el Equipo**

Una vez desplegado, envía este mensaje:

```
🌍 Carbon Footprint Calculator - ¡Ya en línea!

📊 Dashboard Web:
https://carbon-footprint.netlify.app

📖 API Documentación:
https://tu-api.railway.app/docs

❤️ Estado del Sistema:
https://tu-api.railway.app/health

📁 Código Fuente:
https://github.com/TU-USUARIO/carbon-footprint-calculator

📝 Reporte de Validación:
https://github.com/TU-USUARIO/carbon-footprint-calculator/blob/main/REPORTE_VALIDACION.md

---
✅ Sistema validado 100% con datos 2017-2021
🚀 API REST con 8 endpoints documentados
📊 Dashboard interactivo
🔄 Deploy automático desde GitHub
```

---

## 🔧 **Configuración Adicional**

### **Variables de Entorno en Railway**

Si necesitas ajustar configuración:

1. Railway Dashboard → Tu proyecto
2. Variables → New Variable
3. Agregar:
   ```
   PORT=8000
   DATA_DIR=data/raw
   LOG_LEVEL=INFO
   ```

### **Dominio Personalizado** (Opcional)

Railway:
1. Settings → Domains
2. Click "Custom Domain"
3. Agregar tu dominio
4. Configurar DNS según instrucciones

---

## 📊 **Usar la API**

### **Desde Python**

```python
import requests

API_URL = "https://tu-api.railway.app"

# Health check
health = requests.get(f"{API_URL}/health").json()
print(health)

# Calcular huella
result = requests.post(f"{API_URL}/calculate/product", json={
    "sector_index": 15,
    "quantity": 1000000
}).json()

print(f"Huella: {result['data']['total_footprint']} ton CO2eq")
```

### **Desde JavaScript/React**

```javascript
const API_URL = 'https://tu-api.railway.app';

// Fetch data
fetch(`${API_URL}/sectors`)
  .then(response => response.json())
  .then(data => console.log(data));

// Calculate footprint
fetch(`${API_URL}/calculate/product`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    sector_index: 15,
    quantity: 1000000
  })
})
  .then(response => response.json())
  .then(data => console.log(data));
```

### **Desde cURL**

```bash
# Health check
curl https://tu-api.railway.app/health

# Get sectors
curl https://tu-api.railway.app/sectors

# Calculate footprint
curl -X POST https://tu-api.railway.app/calculate/product \
  -H "Content-Type: application/json" \
  -d '{"sector_index": 15, "quantity": 1000000}'
```

---

## 🔄 **Actualización Automática**

Cada vez que hagas push a GitHub:
1. GitHub Actions ejecuta tests
2. Si tests pasan, Railway hace deploy automático
3. Nueva versión disponible en 2-3 minutos

```bash
# Hacer cambios
git add .
git commit -m "Update API"
git push origin main

# Railway detecta y despliega automáticamente
```

---

## 🆘 **Troubleshooting**

### **Railway no inicia**

Revisar logs:
```
Railway Dashboard → Deployments → Click en build → Ver logs
```

Causa común: Variables de entorno faltantes

### **Frontend no conecta con API**

1. Verificar URL en `frontend/index.html` línea 244
2. Verificar CORS en API (ya configurado)
3. Abrir consola del navegador (F12) para ver errores

### **API responde 503**

Datos no cargados. Verificar que archivos Excel estén en `data/raw/`:
- anex-MIP-2021.xlsx
- CAEFM-EA68aVALORADO 2021.xlsx

---

## 💰 **Costos**

- **Railway**: $5/mes incluidos (gratis hasta ese límite)
- **Netlify**: Gratis ilimitado
- **GitHub**: Gratis
- **Total**: $0/mes para uso normal

---

## ✅ **Checklist de Deployment**

- [ ] Código en GitHub
- [ ] Railway configurado y desplegado
- [ ] API responde en /health
- [ ] Frontend desplegado en Netlify
- [ ] URLs compartidas con equipo
- [ ] Documentación accesible
- [ ] Tests pasan

---

## 📞 **Soporte**

- **Railway**: https://railway.app/help
- **Netlify**: https://docs.netlify.com
- **GitHub Issues**: En tu repositorio

---

**🎉 ¡Listo! Tu sistema está en la nube y accesible para todo el equipo.**

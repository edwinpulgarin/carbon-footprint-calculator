# 🔗 Guía para Conectar con GitHub

## Paso 1: Crear Repositorio en GitHub

1. Ir a [GitHub](https://github.com)
2. Click en el botón **"+"** (esquina superior derecha)
3. Seleccionar **"New repository"**
4. Configurar:
   - **Repository name**: `carbon-footprint-calculator` (o el nombre que prefieras)
   - **Description**: `Sistema de cálculo de Huella de Carbono basado en MIP`
   - **Visibility**: Public o Private (según tu preferencia)
   - ⚠️ **NO** marcar "Initialize with README" (ya tenemos uno)
   - ⚠️ **NO** agregar .gitignore (ya tenemos uno)
   - ⚠️ **NO** agregar license (ya tenemos una)
5. Click en **"Create repository"**

## Paso 2: Conectar Repositorio Local con GitHub

Después de crear el repo en GitHub, verás instrucciones. Usa estas:

```bash
# Agregar remote
git remote add origin https://github.com/TU-USUARIO/carbon-footprint-calculator.git

# Verificar remote
git remote -v

# Push del código
git branch -M main
git push -u origin main
```

**Alternativa con SSH** (si tienes SSH configurado):
```bash
git remote add origin git@github.com:TU-USUARIO/carbon-footprint-calculator.git
git branch -M main
git push -u origin main
```

## Paso 3: Verificar en GitHub

1. Refrescar la página de tu repositorio en GitHub
2. Deberías ver todos los archivos:
   - ✅ README.md
   - ✅ src/
   - ✅ tests/
   - ✅ .github/workflows/
   - ✅ Dockerfile
   - ✅ etc.

## Paso 4: Configurar Secrets para CI/CD (Opcional)

Si quieres usar el pipeline de CD (Continuous Deployment):

1. En GitHub, ir a: **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Agregar los siguientes secrets:

   ```
   DOCKER_USERNAME: tu-usuario-dockerhub
   DOCKER_PASSWORD: tu-password-dockerhub
   ```

## Paso 5: Proteger Branch Main (Opcional pero Recomendado)

1. Ir a **Settings** → **Branches**
2. En "Branch protection rules", click **"Add rule"**
3. En "Branch name pattern" escribir: `main`
4. Marcar:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
5. Click **"Create"**

## Paso 6: Agregar Topics (Tags)

1. En la página principal del repo, click en el ⚙️ (Settings) junto a "About"
2. Agregar topics:
   ```
   python
   fastapi
   carbon-footprint
   input-output-analysis
   environmental-economics
   sustainability
   climate-change
   api
   docker
   github-actions
   ```

## Paso 7: Crear Primera Release

```bash
# Crear tag
git tag -a v1.0.0 -m "Release v1.0.0 - Initial stable version"

# Push tag
git push origin v1.0.0
```

Esto activará el workflow de CD automáticamente.

## Comandos Git Útiles para el Futuro

### Workflow Diario

```bash
# Ver estado
git status

# Agregar cambios
git add .

# Commit
git commit -m "Descripción del cambio"

# Push
git push origin main
```

### Crear Feature Branch

```bash
# Crear y cambiar a nueva branch
git checkout -b feature/nueva-funcionalidad

# Hacer cambios y commits
git add .
git commit -m "Add nueva funcionalidad"

# Push de la branch
git push origin feature/nueva-funcionalidad

# Luego crear Pull Request en GitHub
```

### Actualizar desde Main

```bash
# Cambiar a main
git checkout main

# Pull de cambios
git pull origin main

# Volver a tu branch
git checkout feature/mi-branch

# Merge de main
git merge main
```

### Ver Historial

```bash
# Log completo
git log

# Log resumido
git log --oneline

# Ver diferencias
git diff
```

## 🔧 Troubleshooting

### Error: "remote origin already exists"

```bash
# Eliminar remote existente
git remote remove origin

# Agregar nuevo remote
git remote add origin https://github.com/TU-USUARIO/repo.git
```

### Error: Authentication failed

**Opción 1**: Usar Personal Access Token
1. Ir a GitHub Settings → Developer settings → Personal access tokens
2. Generar nuevo token con permisos `repo`
3. Usar el token como password

**Opción 2**: Usar SSH
```bash
# Generar SSH key (si no tienes)
ssh-keygen -t ed25519 -C "tu-email@example.com"

# Copiar la clave pública
cat ~/.ssh/id_ed25519.pub

# Agregarla en GitHub Settings → SSH and GPG keys
```

### Error: Updates were rejected

```bash
# Pull primero
git pull origin main --rebase

# Luego push
git push origin main
```

## 📝 .gitignore Importante

El `.gitignore` ya está configurado para excluir:
- ✅ `data/raw/*.xlsx` - Archivos de datos
- ✅ `venv/` - Entorno virtual
- ✅ `__pycache__/` - Cache de Python
- ✅ `.env` - Variables de entorno
- ✅ Logs y archivos temporales

**⚠️ IMPORTANTE**: NO subir archivos confidenciales o muy grandes.

## 🎯 Estructura Recomendada de Commits

```
feat: agregar nueva funcionalidad
fix: corregir bug
docs: actualizar documentación
style: formateo de código
refactor: refactorizar código
test: agregar tests
chore: tareas de mantenimiento
```

Ejemplos:
```bash
git commit -m "feat: add endpoint for sector comparison"
git commit -m "fix: resolve division by zero in intensity calculation"
git commit -m "docs: update API documentation"
```

## 📊 Badges para README

Actualiza el README.md con tus URLs:

```markdown
[![CI Pipeline](https://github.com/TU-USUARIO/carbon-footprint-calculator/actions/workflows/ci.yml/badge.svg)](https://github.com/TU-USUARIO/carbon-footprint-calculator/actions/workflows/ci.yml)
```

## ✅ Checklist Final

Antes de hacer tu primer push:

- [ ] Verificar que `.gitignore` está configurado
- [ ] Revisar que no hay archivos sensibles (`.env`, datos confidenciales)
- [ ] Confirmar que los tests pasan: `pytest`
- [ ] Verificar que el código está formateado: `black src/`
- [ ] Actualizar README.md con URLs correctas
- [ ] Revisar el historial de commits: `git log`

## 🚀 Después del Push

1. ✅ Verificar que el código está en GitHub
2. ✅ Revisar que los workflows de GitHub Actions se ejecutan
3. ✅ Crear un Release (v1.0.0)
4. ✅ Agregar descripción y topics al repo
5. ✅ Compartir el repositorio

## 📞 Recursos

- [GitHub Docs](https://docs.github.com)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [GitHub Actions Docs](https://docs.github.com/en/actions)

---

**¡Listo!** Tu proyecto está ahora en GitHub y listo para colaboración.

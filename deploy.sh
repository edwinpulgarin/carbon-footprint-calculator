#!/bin/bash

# Script de Deployment Automático
# Soporta: Railway, Render, Google Cloud Run

set -e

echo "========================================="
echo "  Carbon Footprint - Auto Deploy"
echo "========================================="
echo ""

# Función para Railway
deploy_railway() {
    echo "🚂 Deployando en Railway..."

    if ! command -v railway &> /dev/null; then
        echo "❌ Railway CLI no está instalado"
        echo "   Instalarlo con: npm install -g @railway/cli"
        exit 1
    fi

    echo "1. Verificando login..."
    railway whoami || railway login

    echo "2. Inicializando proyecto..."
    railway init || true

    echo "3. Configurando variables..."
    railway variables set PORT=8000
    railway variables set DATA_DIR=data/raw

    echo "4. Desplegando..."
    railway up

    echo ""
    echo "✅ Deploy completado!"
    echo "   Ver URL: railway domain"
    echo "   Ver logs: railway logs"
}

# Función para Render
deploy_render() {
    echo "🔷 Deployando en Render..."

    echo "❌ Render requiere configuración manual desde el dashboard"
    echo ""
    echo "Pasos:"
    echo "1. Ir a: https://render.com"
    echo "2. New → Web Service"
    echo "3. Conectar repositorio GitHub"
    echo "4. Configurar:"
    echo "   - Environment: Docker"
    echo "   - Variables: PORT=8000, DATA_DIR=data/raw"
    echo "5. Deploy"
}

# Función para Google Cloud Run
deploy_gcp() {
    echo "☁️  Deployando en Google Cloud Run..."

    if ! command -v gcloud &> /dev/null; then
        echo "❌ Google Cloud SDK no está instalado"
        echo "   Instalarlo desde: https://cloud.google.com/sdk"
        exit 1
    fi

    echo "1. Login y configuración..."
    gcloud auth login
    echo ""
    echo "Ingresa tu PROJECT_ID:"
    read project_id
    gcloud config set project $project_id

    echo "2. Building imagen..."
    gcloud builds submit --tag gcr.io/$project_id/carbon-api

    echo "3. Desplegando..."
    gcloud run deploy carbon-api \
        --image gcr.io/$project_id/carbon-api \
        --platform managed \
        --region us-central1 \
        --allow-unauthenticated \
        --set-env-vars PORT=8000,DATA_DIR=data/raw

    echo ""
    echo "✅ Deploy completado!"
}

# Menú principal
echo "Selecciona plataforma de deployment:"
echo "1) Railway (Recomendado - Más fácil)"
echo "2) Render"
echo "3) Google Cloud Run"
echo "4) Salir"
echo ""
read -p "Opción [1-4]: " option

case $option in
    1)
        deploy_railway
        ;;
    2)
        deploy_render
        ;;
    3)
        deploy_gcp
        ;;
    4)
        echo "Saliendo..."
        exit 0
        ;;
    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac

echo ""
echo "========================================="
echo "  🎉 Deployment Completado!"
echo "========================================="
echo ""
echo "Próximos pasos:"
echo "1. Verificar que la API responde: /health"
echo "2. Probar endpoints: /docs"
echo "3. Compartir URL con el equipo"
echo ""

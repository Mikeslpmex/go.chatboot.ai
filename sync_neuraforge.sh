#!/bin/bash
# Script para mover archivos y sincronizar repos NeuraforgeAI-Suite → go.develeopers.ai

SOURCE=~/NeuraforgeAI-Suite
TARGET=~/go.develeopers.ai

echo "🚀 Iniciando sincronización entre $SOURCE y $TARGET..."

# Crear estructura si no existe
mkdir -p $TARGET/{src,docs,modules,api,ui,tests}

# Mover archivos clave
mv -v $SOURCE/main.py $TARGET/src/
mv -v $SOURCE/requirements.txt $TARGET/
mv -v $SOURCE/render.yaml $TARGET/
mv -v $SOURCE/Procfile $TARGET/
mv -v $SOURCE/LICENSE $TARGET/
mv -v $SOURCE/README.md $TARGET/docs/
mv -v $SOURCE/api/* $TARGET/api/
mv -v $SOURCE/modules/* $TARGET/modules/
mv -v $SOURCE/ui/* $TARGET/ui/
mv -v $SOURCE/tests/* $TARGET/tests/

# Limpiar archivos temporales
find $SOURCE -type f -name "*.pyc" -delete

# Sincronizar con Git
cd $TARGET
git add .
git commit -m "Sync automático desde NeuraforgeAI-Suite"
git push origin main

echo "✅ Sincronización completa y push enviado a GitHub."

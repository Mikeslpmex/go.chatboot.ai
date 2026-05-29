#!/bin/bash
# Módulo de autoreparación para go.develeopers.ai

TARGET=~/go.develeopers.ai
STRUCTURE=("src" "docs" "modules" "api" "ui" "tests" ".github/workflows")

echo "🛠️ Iniciando autoreparación en $TARGET..."

# Verificar y crear carpetas
for dir in "${STRUCTURE[@]}"; do
  if [ ! -d "$TARGET/$dir" ]; then
    echo "⚠️ Carpeta faltante: $dir → creando..."
    mkdir -p "$TARGET/$dir"
  else
    echo "✔ Carpeta OK: $dir"
  fi
done

# Verificar archivos críticos
CRITICAL=("server.py" "requirements.txt" "Procfile" "render.yaml" ".github/workflows/deploy.yml")

for file in "${CRITICAL[@]}"; do
  if [ ! -f "$TARGET/$file" ]; then
    echo "⚠️ Archivo faltante: $file → creando placeholder..."
    echo "# Autorepair placeholder for $file" > "$TARGET/$file"
  else
    echo "✔ Archivo OK: $file"
  fi
done

# Sincronizar con Git
cd $TARGET
git add .
git commit -m "Autorepair: estructura verificada y corregida"
git push origin main

echo "✅ Autoreparación completa y sincronización con GitHub."

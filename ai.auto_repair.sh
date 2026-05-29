#!/bin/bash
# Autoreparación avanzada para go.develeopers.ai

TARGET=~/go.develeopers.ai
STRUCTURE=("src" "docs" "modules" "api" "ui" "tests" ".github/workflows")

echo "🛠️ Autoreparación iniciada en $TARGET..."

# Verificar carpetas
for dir in "${STRUCTURE[@]}"; do
  if [ ! -d "$TARGET/$dir" ]; then
    echo "⚠️ Falta carpeta: $dir → creando..."
    mkdir -p "$TARGET/$dir"
  fi
done

# Verificar archivos críticos
CRITICAL=("server.py" "requirements.txt" "Procfile" "render.yaml" ".github/workflows/deploy.yml")

for file in "${CRITICAL[@]}"; do
  if [ ! -f "$TARGET/$file" ]; then
    echo "⚠️ Falta archivo: $file → creando placeholder..."
    echo "# Autorepair placeholder for $file" > "$TARGET/$file"
  fi
done

# Sincronizar con Git
cd $TARGET
git add .
git commit -m "Autorepair: estructura verificada y corregida" || echo "Sin cambios que commitear"
git push origin main

echo "✅ Autoreparación completa."

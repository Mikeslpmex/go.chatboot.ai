#!/bin/bash
# Script de configuración inicial para go.develeopers.ai

echo "🚀 Configurando Neuraforge Eternal API..."

# Crear estructura de carpetas
mkdir -p src docs tests modules api ui .github/workflows

# Crear server.py
cat > server.py << 'EOF'
from fastapi import FastAPI

app = FastAPI(title="Neuraforge Eternal API", version="1.0.0")

@app.get("/")
def root():
    return {"message": "Bienvenido a Neuraforge Eternal API — go.develeopers.ai"}

@app.get("/servers")
def servers():
    return {
        "servers": [
            {"id": "srv-001", "name": "Bot Engine", "status": "Running"},
            {"id": "srv-002", "name": "Dashboard", "status": "Stopped"}
        ]
    }

@app.post("/deploy/{app_name}")
def deploy(app_name: str):
    return {"status": "success", "message": f"✔ Deploy completado para {app_name}"}

@app.get("/affiliates")
def affiliates():
    return {"affiliates": ["Stripe", "PayPal", "OpenPay"]}
EOF

# Crear requirements.txt
cat > requirements.txt << 'EOF'
fastapi
uvicorn
EOF

# Crear Procfile
echo "web: uvicorn server:app --host 0.0.0.0 --port \$PORT" > Procfile

# Crear render.yaml
cat > render.yaml << 'EOF'
services:
  - type: web
    name: go-develeopers-ai
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn server:app --host 0.0.0.0 --port $PORT
    plan: free
    autoDeploy: true
EOF

# Crear workflow de GitHub
cat > .github/workflows/deploy.yml << 'EOF'
name: Deploy NeuraforgeAI

on:
  push:
    branches: [ "main" ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

      - name: Deploy to Render
        run: |
          curl -fsSL https://render.com/install.sh | bash
          render deploy --service go-develeopers-ai
EOF

echo "✔ Configuración completa. Ahora haz:"
echo "git add ."
echo "git commit -m 'Setup inicial con API y workflows'"
echo "git push origin main"


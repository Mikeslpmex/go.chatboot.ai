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

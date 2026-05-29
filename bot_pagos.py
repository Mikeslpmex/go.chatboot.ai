from fastapi import FastAPI

app = FastAPI(title="Neuraforge Payments Bot")

# Endpoint para registrar pago
@app.post("/payments")
def register_payment(user_id: str, amount: float, method: str):
    return {
        "status": "success",
        "user_id": user_id,
        "amount": amount,
        "method": method,
        "message": "Pago registrado correctamente"
    }

# Endpoint para listar pagos
@app.get("/payments")
def list_payments():
    return {
        "payments": [
            {"user_id": "u001", "amount": 10.5, "method": "Stripe"},
            {"user_id": "u002", "amount": 25.0, "method": "PayPal"}
        ]
    }

import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import mercadopago

from database import init_db, get_db_connection
from payment_modules import OXXOPayment, GiftCardWallet

load_dotenv()
init_db()

app = Flask(__name__)
CORS(app)  # Permitir peticiones desde frontend

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar módulos
oxxo = OXXOPayment()
sdk = mercadopago.SDK(os.getenv("MERCADO_PAGO_ACCESS_TOKEN"))

# Helper para obtener conexión a DB dentro de rutas
def get_wallet():
    conn = get_db_connection()
    return GiftCardWallet(conn)

# ------------------- RUTAS DE USUARIOS -------------------
@app.route('/api/user/create', methods=['POST'])
def create_user():
    data = request.json
    user_id = data.get('user_id')
    email = data.get('email')
    
    if not user_id or not email:
        return jsonify({"error": "user_id y email requeridos"}), 400
    
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO users (id, email, created_at) VALUES (?, ?, ?)",
            (user_id, email, datetime.now().isoformat())
        )
        conn.commit()
        return jsonify({"success": True, "user_id": user_id})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Usuario ya existe"}), 409
    finally:
        conn.close()

# ------------------- RUTAS DE OXXO -------------------
@app.route('/api/payment/oxxo/create', methods=['POST'])
def create_oxxo():
    data = request.json
    required = ['amount', 'concept', 'email', 'user_id']
    if not all(k in data for k in required):
        return jsonify({"error": "Faltan campos"}), 400
    
    result = oxxo.create_oxxo_reference(
        amount=float(data['amount']),
        concept=data['concept'],
        user_email=data['email'],
        user_id=data['user_id']
    )
    return jsonify(result)

@app.route('/api/payment/oxxo/status/<int:payment_id>', methods=['GET'])
def oxxo_status(payment_id):
    result = oxxo.check_payment_status(payment_id)
    return jsonify(result)

# ------------------- RUTAS DE TARJETAS DE REGALO -------------------
@app.route('/api/gift-card/generate', methods=['POST'])
def generate_gift_card():
    data = request.json
    amount = float(data.get('amount', 0))
    expires_days = int(data.get('expires_days', 365))
    
    if amount <= 0:
        return jsonify({"error": "Monto inválido"}), 400
    
    wallet = get_wallet()
    card = wallet.generate_gift_card(amount, expires_days)
    return jsonify(card)

@app.route('/api/gift-card/redeem', methods=['POST'])
def redeem_gift_card():
    data = request.json
    code = data.get('code')
    pin = data.get('pin')
    user_id = data.get('user_id')
    
    if not all([code, pin, user_id]):
        return jsonify({"error": "Faltan campos"}), 400
    
    wallet = get_wallet()
    result = wallet.redeem_gift_card(code, int(pin), user_id)
    return jsonify(result)

# ------------------- RUTAS DE WALLET (SALDO INTERNO) -------------------
@app.route('/api/wallet/balance/<user_id>', methods=['GET'])
def get_balance(user_id):
    wallet = get_wallet()
    balance = wallet.get_user_balance(user_id)
    return jsonify({"user_id": user_id, "balance": balance})

@app.route('/api/wallet/add', methods=['POST'])
def add_balance():
    data = request.json
    user_id = data.get('user_id')
    amount = float(data.get('amount', 0))
    source = data.get('source', 'admin')
    description = data.get('description', '')
    
    if not user_id or amount <= 0:
        return jsonify({"error": "Datos inválidos"}), 400
    
    wallet = get_wallet()
    result = wallet.add_wallet_balance(user_id, amount, source, description)
    return jsonify(result)

@app.route('/api/wallet/pay', methods=['POST'])
def pay_with_wallet():
    data = request.json
    user_id = data.get('user_id')
    amount = float(data.get('amount', 0))
    concept = data.get('concept', 'Pago interno')
    
    if not user_id or amount <= 0:
        return jsonify({"error": "Datos inválidos"}), 400
    
    wallet = get_wallet()
    result = wallet.pay_with_wallet(user_id, amount, concept)
    return jsonify(result)

# ------------------- WEBHOOK DE MERCADO PAGO -------------------
@app.route('/webhook/mercadopago', methods=['POST'])
def mercadopago_webhook():
    data = request.json
    logger.info(f"Webhook recibido: {data}")
    
    if data.get("type") == "payment":
        payment_id = data["data"]["id"]
        
        # Consultar estado del pago
        payment_info = sdk.payment().get(payment_id)
        
        if payment_info["status"] == 200:
            payment = payment_info["response"]
            status = payment["status"]
            external_ref = payment.get("external_reference", "")
            amount = payment["transaction_amount"]
            
            # Guardar en base de datos
            conn = get_db_connection()
            conn.execute(
                "INSERT OR REPLACE INTO mercadopago_payments (payment_id, amount, status, external_reference, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (payment_id, amount, status, external_ref, payment["date_created"], datetime.now().isoformat())
            )
            conn.commit()
            
            if status == "approved":
                # Extraer user_id del external_reference
                user_id = None
                if external_ref and "_" in external_ref:
                    parts = external_ref.split("_")
                    if len(parts) >= 3:
                        user_id = parts[2]
                
                if user_id:
                    wallet = get_wallet()
                    wallet.add_wallet_balance(
                        user_id, amount, "mercadopago_oxxo",
                        f"Pago OXXO aprobado - Ref: {external_ref}"
                    )
                    logger.info(f"✅ Saldo agregado a {user_id}: ${amount}")
            
            conn.close()
    
    return jsonify({"status": "ok"}), 200

# ------------------- HEALTH CHECK -------------------
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "alive", "version": "1.0"})

# ------------------- INICIAR SERVIDOR -------------------
if __name__ == '__main__':
    port = int(os.getenv("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=False)

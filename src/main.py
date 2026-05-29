from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configura tu API KEY de Google Gemini aquí o en el .env de Render
GENAI_API_KEY = os.getenv("GENAI_API_KEY", "TU_API_KEY_AQUI")
genai.configure(api_key=GENAI_API_KEY)

app = FastAPI(title="NeuraforgeAI Gateway")

# Configuración de Afiliados
MY_PAYPAL = "https://www.paypal.me/TU_CUENTA"
MY_IDS = {
    "hostinger": "NEURAFORGE",
    "shorte": "TU_ID_SHORTE"
}

ERROR_DB = {
    "404": {"name": "404 Not Found", "desc": "Página no encontrada o enlace roto.", "link": "https://neuraforge.ai/solucion404"},
    "500": {"name": "500 Internal Server Error", "desc": "Error crítico del servidor externo.", "link": "https://neuraforge.ai/solucion500"},
    "ssl": {"name": "ERR_SSL_PROTOCOL_ERROR", "desc": "La conexión no es segura o privada.", "link": "https://neuraforge.ai/solucion-ssl"},
    "dns": {"name": "ERR_NAME_NOT_RESOLVED", "desc": "No se encuentra la IP del sitio.", "link": "https://neuraforge.ai/solucion-dns"}
}

class ChatQuery(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
    <head>
        <title>NeuraforgeAI - Nodo de Rescate</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { background:#0a0a0a; color:#00ff00; font-family:monospace; padding:20px; text-align:center; }
            .container { max-width:600px; margin:auto; border:2px solid #00ff00; padding:20px; border-radius:15px; }
            .chat-box { background:#111; border:1px solid #00ff00; height:200px; overflow-y:auto; margin-bottom:10px; padding:10px; text-align:left; }
            input { width:70%; padding:10px; background:#000; color:#0ff; border:1px solid #00ff00; }
            button { padding:10px; background:#00ff00; color:#000; border:none; cursor:pointer; font-weight:bold; }
            .btn-main { display:block; background:#00ff00; color:#000; padding:15px; margin:10px 0; text-decoration:none; font-weight:bold; border-radius:5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔱 NEURAFORGE AI 🔱</h1>
            <p>Moneda: <b>ForgeCoin (FC)</b></p>
            <div class="chat-box" id="chat">Agente Neuraforge: Hola, ¿qué error te aparece en internet?</div>
            <input type="text" id="userInput" placeholder="Escribe tu error aquí...">
            <button onclick="sendMessage()">ENVIAR</button>
            <hr>
            <a class="btn-main" href='https://www.hostinger.com.mx/?referral=""" + MY_IDS['hostinger'] + """'>APOYAR CON HOSTINGER</a>
        </div>
        <script>
            async function sendMessage() {
                const input = document.getElementById('userInput');
                const chat = document.getElementById('chat');
                const userMsg = input.value;
                chat.innerHTML += '<div><b>Tú:</b> ' + userMsg + '</div>';
                
                const response = await fetch('/api/agente', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: userMsg})
                });
                const data = await response.json();
                chat.innerHTML += '<div style="color:#0ff"><b>IA:</b> ' + data.reply + '</div>';
                chat.scrollTop = chat.scrollHeight;
                input.value = '';
            }
        </script>
    </body>
    </html>
    """

@app.post("/api/agente")
async def chat_agente(query: ChatQuery):
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"Eres el experto de NeuraforgeAI. El usuario dice: '{query.message}'. Responde brevemente en español y si detectas un error web, menciónalo."
        response = model.generate_content(prompt)
        return {"reply": response.text}
    except Exception as e:
        return {"reply": "Error conectando con el cerebro de Neuraforge. Revisa tu API Key."}

from fastapi import FastAPI
from src.payments import oxxo

app = FastAPI(title="NeuraForge Suite")
app.include_router(oxxo.router, prefix="/payments", tags=["oxxo"])


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
#!/usr/bin/env python3
"""
NeuraforgeAI - Core Financial Ecosystem
Sistema autosustentable de inteligencia artificial con gestión financiera
"""

import asyncio
import logging
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/neuraforge.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class NeuraforgeCore:
    def __init__(self):
        self.treasury = None
        self.bots = {}
        self.payments = None
        
async def initialize(self):
        """Inicializa todo el ecosistema"""
        logger.info("🌱 Iniciando NeuraforgeAI Core...")

        # 1. Inicializar Tesorería
        from neuraforge.core.treasury import TreasuryManager
        self.treasury = TreasuryManager()
        logger.info("✅ Tesorería inicializada")

        # 2. Inicializar Pagos
        from neuraforge.payments.stripe_handler import StripePaymentProcessor
        self.payments = StripePaymentProcessor(self.treasury)
        logger.info("✅ Pasarela de pagos inicializada")

        # 3. Registrar bots iniciales
        await self.register_bots()
        logger.info("✅ Bots registrados")
        logger.info("🚀 NeuraforgeAI listo para operar")

    async def register_bots(self):
        """Registra bots en el sistema"""
        # Aquí puedes agregar la lógica para registrar tus bots
        # Ejemplo:
        # self.bots["telegram"] = TelegramBot()
        pass
            # Procesar pago real (Stripe/PayPal)
            fc_rate = 10  # 1 USD = 10 FC (configurable)
            fc_amount = amount_usd * fc_rate
            
            # Depositar en el bot específico
            self.treasury.create_wallet(recipient_bot)
            self.treasury.deposit(recipient_bot, fc_amount)
            
            logger.info(f"💰 Transacción procesada: {amount_usd} USD → {fc_amount} FC para {recipient_bot}")
            return {"success": True, "fc_received": fc_amount}
            
        except Exception as e:
            logger.error(f"❌ Error en transacción: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def run(self):
        """Ejecuta el ciclo principal del sistema"""
        while True:
            try:
                # Simular ciclo de trabajo
                logger.info("⏳ Ciclo de trabajo iniciado...")
                
                # Aquí irían las lógicas de tus bots
                for bot_name, bot in self.bots.items():
                    if hasattr(bot, 'work'):
                        await bot.work()
                
                await asyncio.sleep(60)  # Esperar 1 minuto
                
            except KeyboardInterrupt:
                logger.info("🛑 Sistema detenido por usuario")
                break
            except Exception as e:
                logger.error(f"❌ Error en ciclo: {str(e)}")
                await asyncio.sleep(5)
async def main():
    """Función principal"""
    core = NeuraforgeCore()
    
    try:
        await core.initialize()
        await core.run()
    except Exception as e:
        logger.error(f"❌ Error fatal: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
#        logger.info("👋 Sistema finalizad
 (Organización inicial del proyecto)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

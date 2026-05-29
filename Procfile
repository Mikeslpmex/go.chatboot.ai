# Servicio principal: API FastAPI
web: uvicorn main:app --host 0.0.0.0 --port $PORT

# Bot de Telegram (escucha y tickets OXXO)
worker: python bots/telegram_bot.py

# Módulo Tesorero / Wallet ForgeCoin
worker: python tesorero/wallet.py

# Servicio de Ads / Monetización (opcional)
worker: python ads/ads_manager.py

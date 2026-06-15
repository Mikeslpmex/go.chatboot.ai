# Usar una imagen oficial de Python ligera (versión slim para ahorrar memoria)
FROM python:3.11-slim

# Evitar que Python escriba archivos .pyc y forzar salida estándar en consola (ideal para los logs de Render)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar solo el archivo de requerimientos primero (optimiza el caché de construcción)
COPY requirements.txt .

# Instalar dependencias sin guardar caché temporal para mantener el contenedor liviano
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de tu proyecto al contenedor
COPY . .

# Render asigna el puerto dinámicamente a través de la variable $PORT, 
# pero exponer el 8000 es una buena práctica de documentación interna.
EXPOSE 8000

# Comando para arrancar tu bot
CMD ["python", "main.py"]

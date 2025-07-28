# Usar una imagen base de Python
FROM python:3.10-slim

# Instalar curl para health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos de requisitos
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY main.py .

# Exponer el puerto que usa Streamlit
EXPOSE 8501

# Configurar variables de entorno para Streamlit
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Health check
#HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Comando para ejecutar la aplicación
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]

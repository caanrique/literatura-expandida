# ============================================
# Literatura Expandida - Dockerfile
# ============================================
# Container para ejecutar Streamlit en Hugging Face Spaces
# ============================================

# Imagen base de Python
FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (para caché de Docker)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Puerto que usa Streamlit
EXPOSE 8501

# Variable de entorno para Streamlit
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Comando para ejecutar la app
CMD ["streamlit", "run", "studio/literatura_expandida.py"]
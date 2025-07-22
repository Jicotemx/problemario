# Dockerfile para Gestor de Problemas Matemáticos en Render
FROM python:3.10-bullseye

# Establece el directorio de trabajo
WORKDIR /app

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-lang-spanish \
    python3-distutils \
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos de requisitos primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instala dependencias de Python
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos de la aplicación
COPY . .

# Verificación de instalaciones críticas (opcional, puede eliminarse después)
RUN python -c "import distutils; print('distutils OK')" && \
    python -c "import setuptools; print(f'setuptools {setuptools.__version__}')" && \
    pdflatex --version

# Expone el puerto que usa la aplicación
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]

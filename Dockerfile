FROM python:3.10-bullseye

WORKDIR /app

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-lang-spanish \
    python3-distutils \
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos de requisitos
COPY requirements.txt .

# Instala dependencias de Python
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos
COPY . .

# Puerto dinámico para Render
ENV PORT=8000
EXPOSE $PORT

# Comando con manejo de workers
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT} --workers=1 --timeout 120"]

FROM python:3.9-slim

# Çalışma dizinini belirle
WORKDIR /app

# Gereksinimleri yükle
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını kopyala
COPY . /app/

# FastAPI uygulamasını başlat
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

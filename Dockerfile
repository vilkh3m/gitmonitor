# Wybierz bazowy obraz z Pythonem 3.11
FROM python:3.11-slim

# Instalacja Gita
RUN apt-get update && apt-get install -y git && apt-get clean

# Ustaw katalog roboczy
WORKDIR /app

# Instalacja FastAPI i Uvicorn
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj aplikację do obrazu
COPY . .

# Ustawienie domyślnej komendy uruchomienia
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

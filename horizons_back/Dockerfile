FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    git \
    gcc \
    pkg-config \
    libcairo2-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./horizons_timetable /app/libs
RUN pip install --no-cache-dir /app/libs/horizons-core \
                               /app/libs/parsing-poste \
                               /app/libs/parsing-benevole \
                               /app/libs/horizons-genetic

COPY ./horizons_back /app/horizons_back
WORKDIR /app/horizons_back

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
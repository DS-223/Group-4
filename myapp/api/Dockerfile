FROM python:3.10-slim-bullseye

RUN apt-get update && apt-get install -y \
    build-essential libpq-dev libfreetype6-dev libpng-dev libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /backend

COPY requirements.txt .

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8000


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
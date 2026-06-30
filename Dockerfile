FROM python:3.13.14-slim

WORKDIR /project

COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-compile -r requirements.txt

COPY ./app ./app

CMD ["python3", "-m", "app.main"]

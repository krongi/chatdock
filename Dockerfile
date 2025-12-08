# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get upgrade -y

RUN pip install numpy==1.25.0 --no-deps && pip install --upgrade setuptools wheel pip flask && pip install -e .

# RUN pip install --upgrade setuptools wheel pip flask

# RUN pip install numpy==1.25.0 --no-deps

# RUN pip install -e .

CMD ["python", "app.py"]

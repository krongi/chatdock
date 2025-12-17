FROM python:3.10-slim

WORKDIR /app

RUN pip install --upgrade wheel setuptools pip && pip install chatterbox-tts flask gunicorn

CMD ["python", "-m", "gunicorn", "-b", "0.0.0.0:5000", "-w", "4", "--timeout", "600", "app:app"]


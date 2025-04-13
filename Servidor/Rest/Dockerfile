FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask flask-restful requests

EXPOSE 5001

CMD ["python", "rest_app.py"]

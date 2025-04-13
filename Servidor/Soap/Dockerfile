FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask requests

EXPOSE 5000

CMD ["python", "servidor_SOAP.py"]

FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir grpcio grpcio-tools

EXPOSE 50051

CMD ["python", "grpc_server.py"]

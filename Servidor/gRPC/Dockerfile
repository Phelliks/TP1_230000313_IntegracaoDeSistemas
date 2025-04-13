FROM python:3.10-slim

WORKDIR /app

COPY Dependencias.txt .
RUN pip install --no-cache-dir -r Dependencias.txt

COPY gRPC/servidor_gRPC.py .
COPY gRPC/livro.proto .
COPY gRPC/livro_pb2.py .
COPY gRPC/livro_pb2_grpc.py .
COPY XML/livros.xml ./livros.xml

CMD ["python", "servidor_gRPC.py"]

FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask flask-graphql graphene xmlschema

EXPOSE 5002

CMD ["python", "servidor_GraphQL.py"]

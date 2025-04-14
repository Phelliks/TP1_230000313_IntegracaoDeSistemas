# 📚 TP1 - Integração de Sistemas
## 📄 Descrição

Este trabalho prático tem como objetivo explorar a comunicação entre um cliente e um servidor utilizando quatro tecnologias distintas de integração de sistemas:

- **REST**
- **SOAP**
- **gRPC**
- **GraphQL**

Cada uma destas tecnologias é responsável por uma operação diferente sobre um ficheiro XML que armazena os livros.

O sistema foi desenvolvido em Python, com os serviços implementados em containers Docker, e o cliente como uma aplicação gráfica Tkinter que comunica com os diferentes serviços.

## ⚙️ Tecnologias Usadas

- Python 3.10
- Flask
- REST
- SOAP
- gRPC + Protobuf
- Graphene (GraphQL)
- Docker e Docker Compose

## 🚀 Como Correr

### 1. Requisitos

- Docker
- Docker Compose
- Cliente fora do Docker (Tkinter)
- Bibliotecas necessárias (indicadas nas dependencias.txt) <- Estas são instaladas automáticamente pelo docker

### 2. Clonar o repositório

```bash
git clone "Url do repositorio"
cd "Nome do repositorio"
```

### 3. Fazer build e iniciar os serviços com o docker
```bash
sudo docker-compose up --build
```

**⚠️Os serviços arrancam automaticamente e ficam disponíveis nas seguintes portas:⚠️**

| Serviço | Porta |
| --- | --- |
| REST | 5001 |
| SOAP | 8000 |
| gRPC | 50051 |
| GraphQL | 4000 |
### 4. Se os teus serviços e o teu cliente tiverem em máquinas separadas tens de fazer este passo ❗❗❗
Visto que o cliente está fora do docker para ele ser iniciado temos de fazer o seguinte comando:
```bash
cd Cliente
python cliente.py
```
### 4.5. Se os teus serviços e o teu cliente tiverem em máquinas separadas tens de fazer este passo ❗❗❗
Se os serviços estão separados temos primeiro de descobrir qual é o endereço de IP da maquina que tem os serviços.
Após isso temos de entrar no **cliente.py** onde no começo teremos de alterar de localhost para o endereço da maquina que tem os serviços:
![image]([https://github.com/user-attachments/assets/0c1791f8-365e-4ffd-9e92-fe562992de6d](https://media.discordapp.net/attachments/1213526643591872565/1361366251523277004/image.png?ex=67fe7e9f&is=67fd2d1f&hm=dae733d072a543e504754c9a99eb23b800fc09988b79ab80f45e9e8ed387274d&=))
 

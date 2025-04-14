# 📚 TP1 - Integração de Sistemas
## 📄 Descrição
Este trabalho prático tem como objetivo explorar a comunicação entre um cliente e um servidor utilizando quatro tecnologias distintas de integração de sistemas:

- **REST**
- **SOAP**
- **gRPC**
- **GraphQL**

Este sistema é composto por:

- Um cliente com uma interface gráfica desenvolvido com **Tkinter** (fora do Docker)
- Quatro serviços em Python, cada um implementado com uma tecnologia diferente
- Contentores Docker que orquestram os serviços com o **docker-compose**
- Um volume Docker partilhado para garantir a persistência e partilha do ficheiro **livros.xml**

O sistema foi desenvolvido em Python, com os serviços implementados em contentores Docker, e o cliente como uma aplicação gráfica Tkinter que comunica com os diferentes serviços.

## ⚙️ Tecnologias Usadas

- Python 3.10+
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
- Bibliotecas necessárias (indicadas nas ```dependencias.txt```) <- Estas são instaladas automáticamente pelo docker

### 2. Clonar o repositório

```bash
git clone "Url do repositorio"
cd "Nome do repositorio"
```

### 3. Fazer build e iniciar os serviços com o docker
**O ```--build``` apenas tem de ser feito na primeira vez após isso já não é preciso**
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

### 4. Iniciar o cliente
Visto que o cliente está fora do docker temos de instalar as dependencias para ele poder ser iniciado.
```bash
pip install -r Servidor\Dependencias.txt <- se estivermos no root do projeto senão este terá de ser modificado
```
Depois para o inicar temos de fazer o seguinte comando:
```bash
cd Cliente
python cliente.py
```
### 4.5. Se os teus serviços e o teu cliente tiverem em máquinas separadas tens de fazer este passo ❗❗❗
Se os serviços estiverem em máquinas diferentes, temos primeiro de descobrir qual é o endereço IP da máquina que tem os serviços.

Depois disso, é necessário editar o **cliente.py**, onde no início será necessário alterar de **localhost** para o endereço da máquina com os serviços:

![image](https://media.discordapp.net/attachments/1213526643591872565/1361366251523277004/image.png?ex=67fe7e9f&is=67fd2d1f&hm=dae733d072a543e504754c9a99eb23b800fc09988b79ab80f45e9e8ed387274d&=)

# 👨‍💻 Autor
- Ricardo Félix da Silva
- Instituto politécnico de Santarém - Unidade Curricular de Integração de Sistemas
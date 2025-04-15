import tkinter as tk
from tkinter import ttk
import requests
import xml.etree.ElementTree as ET
import grpc
import livro_pb2
import livro_pb2_grpc

# URLs dos serviços
SOAP_URL = "http://localhost:8000/soap"
REST_URL = "http://localhost:5001/REST"
GRPC_HOST = "localhost"
GRPC_PORT = 50051
GRAPHQL_URL = "http://localhost:4000/graphql"

# Função para mostrar resposta no widget de texto
def mostrar_resposta(mensagem):
    text_resposta.configure(state="normal")
    text_resposta.insert("end", mensagem + "\n\n")
    text_resposta.see("end")
    text_resposta.configure(state="disabled")

# Função para limpar os campos de input
def limpar_campos():
    entry_nome.delete(0, "end")
    entry_autor.delete(0, "end")
    entry_preco.delete(0, "end")

# Inserir livro via REST
def enviar_livro():
    nome = entry_nome.get().strip()
    autor = entry_autor.get().strip()
    preco_text = entry_preco.get().strip()

    if not nome or not autor or not preco_text:
        mostrar_resposta("[REST] Erro: Preencha todos os campos.")
        return

    try:
        preco = float(preco_text)
    except ValueError:
        mostrar_resposta("[REST] Erro: O preço deve ser um número.")
        return

    livro = {"nome": nome, "autor": autor, "preco": preco}

    try:
        resposta = requests.post(REST_URL, json=livro)
        if resposta.status_code == 201:
            mostrar_resposta(f"[REST] Livro inserido com sucesso: {livro}")
        else:
            erro = resposta.json().get('erro', 'Erro desconhecido')
            mostrar_resposta(f"[REST] Erro: {erro}")
    except Exception as e:
        mostrar_resposta(f"[REST] Erro de comunicação: {str(e)}")
    limpar_campos()

# Modificar livro via SOAP
def modificar_livro():
    nome = entry_nome.get().strip()
    autor = entry_autor.get().strip()
    preco_text = entry_preco.get().strip()

    if not nome:
        mostrar_resposta("[SOAP] Erro: O nome é obrigatório.")
        return

    preco = None
    if preco_text:
        try:
            preco = float(preco_text)
        except ValueError:
            mostrar_resposta("[SOAP] Erro: O preço deve ser um número.")
            return

    # Criar pedido SOAP manualmente
    envelope = ET.Element("Envelope")
    body = ET.SubElement(envelope, "Body")
    req = ET.SubElement(body, "LivroUpdateRequest")
    ET.SubElement(req, "nome").text = nome
    if autor:
        ET.SubElement(req, "autor").text = autor
    if preco is not None:
        ET.SubElement(req, "preco").text = str(preco)

    xml_str = ET.tostring(envelope, encoding='utf-8')
    headers = {"Content-Type": "application/xml"}

    try:
        resposta = requests.post(SOAP_URL, data=xml_str, headers=headers)
        if resposta.status_code == 200 and "sucesso" in resposta.text.lower():
            mostrar_resposta(f"[SOAP] Livro modificado: {nome}, Autor: {autor}, Preço: {preco}")
        else:
            mostrar_resposta(f"[SOAP] Falha ao modificar livro: {resposta.text}")
    except Exception as e:
        mostrar_resposta(f"[SOAP] Erro de comunicação: {str(e)}")
    limpar_campos()

# Procurar livro via gRPC
def procurar_livro():
    nome = entry_nome.get().strip()
    if not nome:
        mostrar_resposta("[gRPC] Erro: Introduza o nome do livro.")
        return

    try:
        with grpc.insecure_channel(f"{GRPC_HOST}:{GRPC_PORT}") as channel:
            stub = livro_pb2_grpc.LivroServiceStub(channel)
            request = livro_pb2.LivroRequest(nome=nome)
            response = stub.ProcurarLivro(request)

            resultado = f"[gRPC] Resultado:\nNome: {response.nome}\nAutor: {response.autor}\nPreço: {response.preco:.2f}€"
            mostrar_resposta(resultado)
    except grpc.RpcError as e:
        erro = e.details() if hasattr(e, 'details') else str(e)
        mostrar_resposta(f"[gRPC] Erro: {erro}")
    limpar_campos()

# Eliminar livro via GraphQL
def eliminar_livro():
    nome = entry_nome.get().strip()
    if not nome:
        mostrar_resposta("[GraphQL] Erro: Introduza o nome do livro.")
        return

    query = {
        "query": f"""
        mutation {{
            eliminarLivro(nome: \"{nome}\") {{
                sucesso
                mensagem
            }}
        }}
        """
    }

    try:
        resposta = requests.post(GRAPHQL_URL, json=query)
        dados = resposta.json()

        if "errors" in dados:
            erro = dados['errors'][0]['message']
            mostrar_resposta(f"[GraphQL] Erro: {erro}")
            return

        resultado = dados["data"]["eliminarLivro"]
        mostrar_resposta(f"[GraphQL] {resultado['mensagem']}")
    except Exception as e:
        mostrar_resposta(f"[GraphQL] Erro de comunicação: {str(e)}")
    limpar_campos()

#==============================================
# Interface Gráfica (com campos partilhados)
#==============================================
root = tk.Tk()
root.title("Cliente Livros - REST, SOAP, gRPC, GraphQL")

frame = ttk.Frame(root, padding=10)
frame.pack(fill="both", expand=True)

# Campos comuns
ttk.Label(frame, text="Nome:").grid(row=0, column=0, sticky="w")
entry_nome = ttk.Entry(frame)
entry_nome.grid(row=0, column=1, sticky="ew")

ttk.Label(frame, text="Autor:").grid(row=1, column=0, sticky="w")
entry_autor = ttk.Entry(frame)
entry_autor.grid(row=1, column=1, sticky="ew")

ttk.Label(frame, text="Preço:").grid(row=2, column=0, sticky="w")
entry_preco = ttk.Entry(frame)
entry_preco.grid(row=2, column=1, sticky="ew")

# Botões de ação
ttk.Button(frame, text="Inserir Livro (REST)", command=enviar_livro).grid(row=3, column=0, columnspan=2, sticky="ew", pady=2)
ttk.Button(frame, text="Modificar Livro (SOAP)", command=modificar_livro).grid(row=4, column=0, columnspan=2, sticky="ew", pady=2)
ttk.Button(frame, text="Procurar Livro (gRPC)", command=procurar_livro).grid(row=5, column=0, columnspan=2, sticky="ew", pady=2)
ttk.Button(frame, text="Eliminar Livro (GraphQL)", command=eliminar_livro).grid(row=6, column=0, columnspan=2, sticky="ew", pady=2)

# Área de resposta
text_resposta = tk.Text(frame, height=12, wrap="word", state="disabled", bg="#f0f0f0")
text_resposta.grid(row=7, column=0, columnspan=2, pady=10, sticky="nsew")

# Permitir expansão
frame.columnconfigure(1, weight=1)
frame.rowconfigure(7, weight=1)

root.mainloop()

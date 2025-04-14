import tkinter as tk
from tkinter import ttk
import requests
import xml.etree.ElementTree as ET
import grpc
import livro_pb2
import livro_pb2_grpc

SOAP_URL = "http://localhost:8000/soap"
REST_URL = "http://localhost:5001/REST"
GRPC_HOST = "localhost"
GRPC_PORT = 50051
GRAPHQL_URL = "http://localhost:4000/graphql"

def mostrar_resposta(text_widget, mensagem):
    text_widget.configure(state="normal")
    text_widget.insert("end", mensagem + "\n\n")
    text_widget.see("end")
    text_widget.configure(state="disabled")

def enviar_livro():
    nome = entry_ins_nome.get().strip()
    autor = entry_ins_autor.get().strip()
    preco_text = entry_ins_preco.get().strip()

    if not nome or not autor or not preco_text:
        mostrar_resposta(text_ins_resposta, "[REST] Erro: Preencha todos os campos.")
        return

    try:
        preco = float(preco_text)
    except ValueError:
        mostrar_resposta(text_ins_resposta, "[REST] Erro: O preço deve ser um número.")
        return

    livro = {"nome": nome, "autor": autor, "preco": preco}

    try:
        resposta = requests.post(REST_URL, json=livro)
        if resposta.status_code == 201:
            mostrar_resposta(text_ins_resposta, f"[REST] Livro inserido com sucesso: {livro}")
        else:
            erro = resposta.json().get('erro', 'Erro desconhecido')
            mostrar_resposta(text_ins_resposta, f"[REST] Erro: {erro}")
    except Exception as e:
        mostrar_resposta(text_ins_resposta, f"[REST] Erro de comunicação: {str(e)}")

def modificar_livro():
    nome = entry_mod_nome.get().strip()
    autor = entry_mod_autor.get().strip()
    preco_text = entry_mod_preco.get().strip()

    if not nome:
        mostrar_resposta(text_mod_resposta, "[SOAP] Erro: O nome é obrigatório.")
        return

    preco = None
    if preco_text:
        try:
            preco = float(preco_text)
        except ValueError:
            mostrar_resposta(text_mod_resposta, "[SOAP] Erro: O preço deve ser um número.")
            return

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
            mostrar_resposta(text_mod_resposta, f"[SOAP] Livro modificado: {nome}, Autor: {autor}, Preço: {preco}")
        else:
            mostrar_resposta(text_mod_resposta, f"[SOAP] Falha ao modificar livro: {resposta.text}")
    except Exception as e:
        mostrar_resposta(text_mod_resposta, f"[SOAP] Erro de comunicação: {str(e)}")

def procurar_livro():
    nome = entry_procura_nome.get().strip()
    if not nome:
        mostrar_resposta(text_proc_resposta, "[gRPC] Erro: Introduza o nome do livro.")
        return

    try:
        with grpc.insecure_channel(f"{GRPC_HOST}:{GRPC_PORT}") as channel:
            stub = livro_pb2_grpc.LivroServiceStub(channel)
            request = livro_pb2.LivroRequest(nome=nome)
            response = stub.ProcurarLivro(request)

            resultado = f"[gRPC] Resultado:\nNome: {response.nome}\nAutor: {response.autor}\nPreço: {response.preco:.2f}€"
            mostrar_resposta(text_proc_resposta, resultado)
    except grpc.RpcError as e:
        erro = e.details() if hasattr(e, 'details') else str(e)
        mostrar_resposta(text_proc_resposta, f"[gRPC] Erro: {erro}")

def eliminar_livro():
    nome = entry_eliminar_nome.get().strip()
    if not nome:
        mostrar_resposta(text_eli_resposta, "[GraphQL] Erro: Introduza o nome do livro.")
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
            mostrar_resposta(text_eli_resposta, f"[GraphQL] Erro: {erro}")
            return

        resultado = dados["data"]["eliminarLivro"]
        mostrar_resposta(text_eli_resposta, f"[GraphQL] {resultado['mensagem']}")
    except Exception as e:
        mostrar_resposta(text_eli_resposta, f"[GraphQL] Erro de comunicação: {str(e)}")

# Interface gráfica
root = tk.Tk()
root.title("Cliente Livros - REST, SOAP, gRPC, GraphQL")

notebook = ttk.Notebook(root)
notebook.pack(padx=10, pady=10, expand=True, fill="both")

# Aba REST
aba_inserir = ttk.Frame(notebook)
notebook.add(aba_inserir, text="Inserir Livro (REST)")
frame_ins = ttk.Frame(aba_inserir)
frame_ins.pack(padx=10, pady=10, fill="x")
entry_ins_nome = ttk.Entry(frame_ins)
entry_ins_autor = ttk.Entry(frame_ins)
entry_ins_preco = ttk.Entry(frame_ins)
ttk.Label(frame_ins, text="Nome:").grid(row=0, column=0, sticky="w")
entry_ins_nome.grid(row=0, column=1)
ttk.Label(frame_ins, text="Autor:").grid(row=1, column=0, sticky="w")
entry_ins_autor.grid(row=1, column=1)
ttk.Label(frame_ins, text="Preço:").grid(row=2, column=0, sticky="w")
entry_ins_preco.grid(row=2, column=1)
ttk.Button(frame_ins, text="Inserir Livro", command=enviar_livro).grid(row=3, columnspan=2, pady=5)
text_ins_resposta = tk.Text(aba_inserir, height=10, wrap="word", state="disabled", bg="#f0f0f0")
text_ins_resposta.pack(padx=10, pady=10, expand=True, fill="both")

# Aba SOAP
aba_modificar = ttk.Frame(notebook)
notebook.add(aba_modificar, text="Modificar Livro (SOAP)")
frame_mod = ttk.Frame(aba_modificar)
frame_mod.pack(padx=10, pady=10, fill="x")
entry_mod_nome = ttk.Entry(frame_mod)
entry_mod_autor = ttk.Entry(frame_mod)
entry_mod_preco = ttk.Entry(frame_mod)
ttk.Label(frame_mod, text="Nome:").grid(row=0, column=0, sticky="w")
entry_mod_nome.grid(row=0, column=1)
ttk.Label(frame_mod, text="Novo Autor:").grid(row=1, column=0, sticky="w")
entry_mod_autor.grid(row=1, column=1)
ttk.Label(frame_mod, text="Novo Preço:").grid(row=2, column=0, sticky="w")
entry_mod_preco.grid(row=2, column=1)
ttk.Button(frame_mod, text="Modificar Livro", command=modificar_livro).grid(row=3, columnspan=2, pady=5)
text_mod_resposta = tk.Text(aba_modificar, height=10, wrap="word", state="disabled", bg="#f0f0f0")
text_mod_resposta.pack(padx=10, pady=10, expand=True, fill="both")

# Aba gRPC
aba_procurar = ttk.Frame(notebook)
notebook.add(aba_procurar, text="Procurar Livro (gRPC)")
frame_proc = ttk.Frame(aba_procurar)
frame_proc.pack(padx=10, pady=10, fill="x")
entry_procura_nome = ttk.Entry(frame_proc)
ttk.Label(frame_proc, text="Nome do Livro:").grid(row=0, column=0, sticky="w")
entry_procura_nome.grid(row=0, column=1)
ttk.Button(frame_proc, text="Procurar", command=procurar_livro).grid(row=1, columnspan=2, pady=5)
text_proc_resposta = tk.Text(aba_procurar, height=10, wrap="word", state="disabled", bg="#f0f0f0")
text_proc_resposta.pack(padx=10, pady=10, expand=True, fill="both")

# Aba GraphQL
aba_eliminar = ttk.Frame(notebook)
notebook.add(aba_eliminar, text="Eliminar Livro (GraphQL)")
frame_eli = ttk.Frame(aba_eliminar)
frame_eli.pack(padx=10, pady=10, fill="x")
entry_eliminar_nome = ttk.Entry(frame_eli)
ttk.Label(frame_eli, text="Nome do Livro:").grid(row=0, column=0, sticky="w")
entry_eliminar_nome.grid(row=0, column=1)
ttk.Button(frame_eli, text="Eliminar", command=eliminar_livro).grid(row=1, columnspan=2, pady=5)
text_eli_resposta = tk.Text(aba_eliminar, height=10, wrap="word", state="disabled", bg="#f0f0f0")
text_eli_resposta.pack(padx=10, pady=10, expand=True, fill="both")

root.mainloop()

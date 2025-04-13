import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import xml.etree.ElementTree as ET
import grpc
import livro_pb2
import livro_pb2_grpc

# Configuração dos endpoints
SOAP_URL = "http://127.0.0.1:5000/soap"
REST_URL = "http://127.0.0.1:5001/REST"
GRPC_HOST = "localhost"
GRPC_PORT = 50051
GRAPHQL_URL = "http://127.0.0.1:5002/graphql"

# Função para inserir livro via REST
def enviar_livro():
    nome = entry_ins_nome.get().strip()
    autor = entry_ins_autor.get().strip()
    preco_text = entry_ins_preco.get().strip()

    if not nome or not autor or not preco_text:
        messagebox.showwarning("Entrada Inválida", "Preencha todos os campos de inserção.")
        return

    try:
        preco = float(preco_text)
    except ValueError:
        messagebox.showwarning("Valor Inválido", "O preço deve ser um número.")
        return

    livro = {
        "nome": nome,
        "autor": autor,
        "preco": preco
    }

    try:
        resposta = requests.post(REST_URL, json=livro)
        if resposta.status_code == 201:
            messagebox.showinfo("Sucesso", "Livro inserido com sucesso!")
        else:
            messagebox.showerror("Erro", f"Erro ao inserir livro: {resposta.json().get('erro')}")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao comunicar com o servidor REST: {str(e)}")

# Função para modificar livro via SOAP
def modificar_livro():
    nome = entry_mod_nome.get().strip()
    autor = entry_mod_autor.get().strip()
    preco_text = entry_mod_preco.get().strip()

    if not nome:
        messagebox.showwarning("Entrada Inválida", "O nome do livro é obrigatório para modificação.")
        return

    preco = None
    if preco_text:
        try:
            preco = float(preco_text)
        except ValueError:
            messagebox.showwarning("Valor Inválido", "O preço deve ser um número.")
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
            messagebox.showinfo("Sucesso", "Livro modificado com sucesso!")
        else:
            messagebox.showerror("Erro", "Não foi possível modificar o livro.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao comunicar com o servidor SOAP: {str(e)}")

# Função para procurar livro via gRPC
def procurar_livro():
    nome = entry_procura_nome.get().strip()
    if not nome:
        messagebox.showwarning("Entrada Inválida", "Introduza o nome do livro a procurar.")
        return

    try:
        with grpc.insecure_channel(f"{GRPC_HOST}:{GRPC_PORT}") as channel:
            stub = livro_pb2_grpc.LivroServiceStub(channel)
            request = livro_pb2.LivroRequest(nome=nome)
            response = stub.ProcurarLivro(request)

            resultado = f"Nome: {response.nome}\nAutor: {response.autor}\nPreço: {response.preco:.2f}€"
            messagebox.showinfo("Livro Encontrado", resultado)

    except grpc.RpcError as e:
        messagebox.showerror("Erro gRPC", f"Erro ao procurar livro: {e.details() if hasattr(e, 'details') else str(e)}")

# Função para eliminar livro via GraphQL
def eliminar_livro():
    nome = entry_eliminar_nome.get().strip()
    if not nome:
        messagebox.showwarning("Entrada Inválida", "Introduza o nome do livro a eliminar.")
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
            messagebox.showerror("Erro", f"Erro do servidor GraphQL: {dados['errors'][0]['message']}")
            return

        resultado = dados["data"]["eliminarLivro"]
        if resultado["sucesso"]:
            messagebox.showinfo("Sucesso", resultado["mensagem"])
        else:
            messagebox.showwarning("Não Encontrado", resultado["mensagem"])

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao comunicar com o servidor GraphQL: {str(e)}")

# Interface Gráfica
root = tk.Tk()
root.title("Cliente Livros - REST, SOAP, gRPC e GraphQL")

notebook = ttk.Notebook(root)
notebook.pack(padx=10, pady=10, expand=True, fill="both")

# Aba Inserir
aba_inserir = ttk.Frame(notebook)
notebook.add(aba_inserir, text="Inserir Livro (REST)")

frame_ins = ttk.Frame(aba_inserir)
frame_ins.pack(padx=10, pady=10, fill="x")

entry_ins_nome = ttk.Entry(frame_ins)
entry_ins_autor = ttk.Entry(frame_ins)
entry_ins_preco = ttk.Entry(frame_ins)

ttk.Label(frame_ins, text="Nome:").grid(row=0, column=0, sticky="w")
entry_ins_nome.grid(row=0, column=1, pady=2)

ttk.Label(frame_ins, text="Autor:").grid(row=1, column=0, sticky="w")
entry_ins_autor.grid(row=1, column=1, pady=2)

ttk.Label(frame_ins, text="Preço:").grid(row=2, column=0, sticky="w")
entry_ins_preco.grid(row=2, column=1, pady=2)

ttk.Button(frame_ins, text="Inserir Livro", command=enviar_livro).grid(row=3, columnspan=2, pady=5)

# Aba Modificar
aba_modificar = ttk.Frame(notebook)
notebook.add(aba_modificar, text="Modificar Livro (SOAP)")

frame_mod = ttk.Frame(aba_modificar)
frame_mod.pack(padx=10, pady=10, fill="x")

entry_mod_nome = ttk.Entry(frame_mod)
entry_mod_autor = ttk.Entry(frame_mod)
entry_mod_preco = ttk.Entry(frame_mod)

ttk.Label(frame_mod, text="Nome:").grid(row=0, column=0, sticky="w")
entry_mod_nome.grid(row=0, column=1, pady=2)

ttk.Label(frame_mod, text="Novo Autor:").grid(row=1, column=0, sticky="w")
entry_mod_autor.grid(row=1, column=1, pady=2)

ttk.Label(frame_mod, text="Novo Preço:").grid(row=2, column=0, sticky="w")
entry_mod_preco.grid(row=2, column=1, pady=2)

ttk.Button(frame_mod, text="Modificar Livro", command=modificar_livro).grid(row=3, columnspan=2, pady=5)

# Aba Procurar
tt_frame = ttk.Frame(notebook)
notebook.add(tt_frame, text="Procurar Livro (gRPC)")

frame_proc = ttk.Frame(tt_frame)
frame_proc.pack(padx=10, pady=10, fill="x")

entry_procura_nome = ttk.Entry(frame_proc)

ttk.Label(frame_proc, text="Nome do Livro:").grid(row=0, column=0, sticky="w")
entry_procura_nome.grid(row=0, column=1, pady=2)

ttk.Button(frame_proc, text="Procurar", command=procurar_livro).grid(row=1, columnspan=2, pady=5)

# Aba Eliminar
aba_eliminar = ttk.Frame(notebook)
notebook.add(aba_eliminar, text="Eliminar Livro (GraphQL)")

frame_eli = ttk.Frame(aba_eliminar)
frame_eli.pack(padx=10, pady=10, fill="x")

entry_eliminar_nome = ttk.Entry(frame_eli)

ttk.Label(frame_eli, text="Nome do Livro:").grid(row=0, column=0, sticky="w")
entry_eliminar_nome.grid(row=0, column=1, pady=2)

ttk.Button(frame_eli, text="Eliminar", command=eliminar_livro).grid(row=1, columnspan=2, pady=5)

root.mainloop()
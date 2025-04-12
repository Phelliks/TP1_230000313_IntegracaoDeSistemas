import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from jsonschema import validate, ValidationError
from jsonpath_ng import parse
import xml.etree.ElementTree as ET

# Configurações dos endpoints:
SOAP_URL = "http://127.0.0.1:5000/soap"
REST_URL = "http://127.0.0.1:5001/REST"

# JSON Schema para validação dos dados do livro (usado pelo REST)
book_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "nome": {"type": "string"},
        "autor": {"type": "string"},
        "preco": {"type": "number"}
    },
    "required": ["nome", "autor", "preco"]
}

def enviar_livro():
    protocolo = protocolo_var.get()
    nome = entry_ins_nome.get().strip()
    autor = entry_ins_autor.get().strip()
    preco_text = entry_ins_preco.get().strip()

    if not nome or not autor or not preco_text:
        messagebox.showwarning("Entrada Inválida", "Preencha todos os campos de inserção.")
        return
    try:
        preco = float(preco_text)
    except ValueError:
        messagebox.showwarning("Entrada Inválida", "Preço deve ser um número.")
        return

    if protocolo == "REST":
        # Monta o objeto JSON e valida
        livro = {"nome": nome, "autor": autor, "preco": preco}
        try:
            validate(instance=livro, schema=book_schema)
        except ValidationError as ve:
            messagebox.showerror("Erro de Validação", f"Erro no JSON: {ve.message}")
            return
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(REST_URL, json=livro, headers=headers)
            if response.status_code == 201:
                label_ins_result.config(text="Livro inserido via REST: Sucesso!")
            else:
                try:
                    err_msg = response.json().get("erro", response.text)
                except Exception:
                    err_msg = response.text
                label_ins_result.config(text=f"Erro REST: {err_msg}")
        except Exception as e:
            label_ins_result.config(text=f"Erro REST: {str(e)}")
    elif protocolo == "SOAP":
        # Monta a mensagem SOAP de inserção
        soap_request = f"""<?xml version="1.0" encoding="UTF-8"?>
<Envelope>
  <Body>
    <LivroRequest>
      <nome>{nome}</nome>
      <autor>{autor}</autor>
      <preco>{preco}</preco>
    </LivroRequest>
  </Body>
</Envelope>"""
        headers = {"Content-Type": "text/xml"}
        try:
            response = requests.post(SOAP_URL, data=soap_request, headers=headers)
            root_resp = ET.fromstring(response.text)
            msg_elem = root_resp.find(".//mensagem")
            if msg_elem is not None:
                label_ins_result.config(text=f"Resposta SOAP: {msg_elem.text}")
            else:
                fault_elem = root_resp.find(".//faultstring")
                if fault_elem is not None:
                    label_ins_result.config(text=f"Erro SOAP: {fault_elem.text}")
                else:
                    label_ins_result.config(text="Erro SOAP: Resposta inválida.")
        except Exception as e:
            label_ins_result.config(text=f"Erro SOAP: {str(e)}")
    else:
        label_ins_result.config(text="Protocolo não reconhecido.")

def consultar_livro():
    protocolo = protocolo_var.get()
    consulta = entry_cons_nome.get().strip()
    jsonpath_query = entry_jsonpath.get().strip()

    if protocolo == "REST":
        try:
            response = requests.get(REST_URL)
            if response.status_code == 200:
                livros_resp = response.json()
                filtered = livros_resp
                # Se foi fornecida uma consulta JSONPath, aplica-a
                if jsonpath_query:
                    try:
                        expr = parse(jsonpath_query)
                        matches = expr.find(livros_resp)
                        filtered = [match.value for match in matches]
                    except Exception as e:
                        label_cons_result.config(text=f"Erro na JSONPath query: {str(e)}")
                        return
                # Se consulta (nome) for fornecida, filtra pelo nome (case insensitive)
                elif consulta:
                    filtered = [b for b in livros_resp if b.get("nome", "").lower() == consulta.lower()]
                if filtered:
                    result_str = "Livros encontrados:\n"
                    for book in filtered:
                        result_str += f"Nome: {book.get('nome')}, Autor: {book.get('autor')}, Preço: {book.get('preco')}\n"
                    label_cons_result.config(text=result_str)
                else:
                    label_cons_result.config(text="Nenhum livro encontrado.")
            else:
                label_cons_result.config(text=f"Erro REST: {response.text}")
        except Exception as e:
            label_cons_result.config(text=f"Erro REST: {str(e)}")
    elif protocolo == "SOAP":
        # Monta a mensagem SOAP para consulta
        soap_request = f"""<?xml version="1.0" encoding="UTF-8"?>
<Envelope>
  <Body>
    <LivroConsultaRequest>
      <nome>{consulta}</nome>
    </LivroConsultaRequest>
  </Body>
</Envelope>"""
        headers = {"Content-Type": "text/xml"}
        try:
            response = requests.post(SOAP_URL, data=soap_request, headers=headers)
            root_resp = ET.fromstring(response.text)
            resp_elem = root_resp.find(".//LivroConsultaResponse")
            if resp_elem is not None:
                nome = resp_elem.findtext("nome")
                autor = resp_elem.findtext("autor")
                preco = resp_elem.findtext("preco")
                label_cons_result.config(text=f"Resultado SOAP:\nNome: {nome}\nAutor: {autor}\nPreço: {preco}")
            else:
                fault_elem = root_resp.find(".//faultstring")
                if fault_elem is not None:
                    label_cons_result.config(text=f"Erro SOAP: {fault_elem.text}")
                else:
                    label_cons_result.config(text="Erro SOAP: Resposta inválida.")
        except Exception as e:
            label_cons_result.config(text=f"Erro SOAP: {str(e)}")
    else:
        label_cons_result.config(text="Protocolo não reconhecido.")

def atualizar_livro():
    protocolo = protocolo_var.get()
    nome = entry_up_nome.get().strip()
    novo_preco_text = entry_up_preco.get().strip()
    if not nome or not novo_preco_text:
        messagebox.showwarning("Entrada Inválida", "Preencha o nome e o novo preço do livro.")
        return
    try:
        novo_preco = float(novo_preco_text)
    except ValueError:
        messagebox.showwarning("Entrada Inválida", "Novo preço deve ser um número.")
        return

    if protocolo == "REST":
        payload = {"nome": nome, "preco": novo_preco}
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.put(REST_URL, json=payload, headers=headers)
            if response.status_code == 200:
                label_up_result.config(text="Livro atualizado via REST com sucesso!")
            else:
                try:
                    err_msg = response.json().get("erro", response.text)
                except Exception:
                    err_msg = response.text
                label_up_result.config(text=f"Erro REST: {err_msg}")
        except Exception as e:
            label_up_result.config(text=f"Erro REST: {str(e)}")
    elif protocolo == "SOAP":
        # Monta a mensagem SOAP para atualização
        soap_request = f"""<?xml version="1.0" encoding="UTF-8"?>
<Envelope>
  <Body>
    <LivroUpdateRequest>
      <nome>{nome}</nome>
      <preco>{novo_preco}</preco>
    </LivroUpdateRequest>
  </Body>
</Envelope>"""
        headers = {"Content-Type": "text/xml"}
        try:
            response = requests.post(SOAP_URL, data=soap_request, headers=headers)
            root_resp = ET.fromstring(response.text)
            msg_elem = root_resp.find(".//mensagem")
            if msg_elem is not None:
                label_up_result.config(text=f"Resposta SOAP: {msg_elem.text}")
            else:
                fault_elem = root_resp.find(".//faultstring")
                if fault_elem is not None:
                    label_up_result.config(text=f"Erro SOAP: {fault_elem.text}")
                else:
                    label_up_result.config(text="Erro SOAP: Resposta inválida.")
        except Exception as e:
            label_up_result.config(text=f"Erro SOAP: {str(e)}")
    else:
        label_up_result.config(text="Protocolo não reconhecido.")

# Criação da janela principal
root = tk.Tk()
root.title("Cliente Integrado: REST / SOAP - Livros")

# Seção para selecionar o protocolo (REST ou SOAP)
frame_protocol = ttk.Frame(root, padding="10")
frame_protocol.pack(fill="x")
ttk.Label(frame_protocol, text="Protocolo:").pack(side="left", padx=5)
protocolo_var = tk.StringVar(value="REST")
combo_protocol = ttk.Combobox(frame_protocol, textvariable=protocolo_var, state="readonly", width=10)
combo_protocol['values'] = ("REST", "SOAP")
combo_protocol.pack(side="left", padx=5)

# Notebook para as operações: Inserir, Consultar e Atualizar
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

### Aba Inserir Livro ###
frame_inserir = ttk.Frame(notebook, padding="10")
notebook.add(frame_inserir, text="Inserir Livro")

ttk.Label(frame_inserir, text="Nome do Livro:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
entry_ins_nome = ttk.Entry(frame_inserir, width=30)
entry_ins_nome.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_inserir, text="Autor:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
entry_ins_autor = ttk.Entry(frame_inserir, width=30)
entry_ins_autor.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(frame_inserir, text="Preço (ex: 29.90):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
entry_ins_preco = ttk.Entry(frame_inserir, width=15)
entry_ins_preco.grid(row=2, column=1, padx=5, pady=5)

btn_inserir = ttk.Button(frame_inserir, text="Inserir Livro", command=enviar_livro)
btn_inserir.grid(row=3, column=0, columnspan=2, pady=10)
label_ins_result = ttk.Label(frame_inserir, text="Resultado Inserção:", font=("Arial", 10))
label_ins_result.grid(row=4, column=0, columnspan=2, pady=10)

### Aba Consultar Livro ###
frame_consultar = ttk.Frame(notebook, padding="10")
notebook.add(frame_consultar, text="Consultar Livro")

ttk.Label(frame_consultar, text="Nome do Livro (opcional):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
entry_cons_nome = ttk.Entry(frame_consultar, width=30)
entry_cons_nome.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_consultar, text="JSONPath Query (opcional):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
entry_jsonpath = ttk.Entry(frame_consultar, width=30)
entry_jsonpath.grid(row=1, column=1, padx=5, pady=5)

btn_consultar = ttk.Button(frame_consultar, text="Consultar Livro", command=consultar_livro)
btn_consultar.grid(row=2, column=0, columnspan=2, pady=10)
label_cons_result = ttk.Label(frame_consultar, text="Resultado Consulta:", font=("Arial", 10))
label_cons_result.grid(row=3, column=0, columnspan=2, pady=10)

### Aba Atualizar Livro ###
frame_update = ttk.Frame(notebook, padding="10")
notebook.add(frame_update, text="Atualizar Livro")

ttk.Label(frame_update, text="Nome do Livro:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
entry_up_nome = ttk.Entry(frame_update, width=30)
entry_up_nome.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_update, text="Novo Preço:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
entry_up_preco = ttk.Entry(frame_update, width=15)
entry_up_preco.grid(row=1, column=1, padx=5, pady=5)

btn_atualizar = ttk.Button(frame_update, text="Atualizar Livro", command=atualizar_livro)
btn_atualizar.grid(row=2, column=0, columnspan=2, pady=10)
label_up_result = ttk.Label(frame_update, text="Resultado Atualização:", font=("Arial", 10))
label_up_result.grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()

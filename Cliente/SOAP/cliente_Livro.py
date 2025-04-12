import tkinter as tk
from tkinter import ttk, messagebox
import requests
import xml.etree.ElementTree as ET

# URL do serviço SOAP (certifique-se de que o servidor esteja rodando)
SOAP_URL = "http://127.0.0.1:5000/soap"

def enviar_livro():
    try:
        # Obter os dados da interface
        nome = entry_nome.get().strip()
        autor = entry_autor.get().strip()
        preco_text = entry_preco.get().strip()
        
        # Verificar se os campos não estão vazios
        if not nome or not autor or not preco_text:
            messagebox.showwarning("Entrada Inválida", "Por favor, preencha todos os campos.")
            return
        
        # Converter o preço para float
        try:
            preco = float(preco_text)
        except ValueError:
            messagebox.showwarning("Entrada Inválida", "Preço deve ser um número (por exemplo, 29.90).")
            return
        
        # Construir a mensagem SOAP conforme o XSD para LivroRequest
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
        response = requests.post(SOAP_URL, data=soap_request, headers=headers)
        
        # Processar a resposta: tentar extrair <mensagem> dentro de <LivroResponse>
        root_resp = ET.fromstring(response.text)
        msg_elem = root_resp.find(".//mensagem")
        
        if msg_elem is not None:
            label_result.config(text=f"Resposta: {msg_elem.text}")
        else:
            # Se não encontrou <mensagem>, tenta extrair mensagem de erro do Fault
            fault_elem = root_resp.find(".//faultstring")
            if fault_elem is not None:
                label_result.config(text=f"Erro: {fault_elem.text}")
            else:
                label_result.config(text="Erro: Resposta não reconhecida.")
    except Exception as e:
        label_result.config(text=f"Erro: {str(e)}")

# Criar a janela principal
root = tk.Tk()
root.title("Cliente SOAP - Cadastro de Livros")

# Configuração do layout
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Label e entry para Nome do Livro
ttk.Label(frame, text="Nome do Livro:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
entry_nome = ttk.Entry(frame, width=30)
entry_nome.grid(row=0, column=1, padx=5, pady=5)

# Label e entry para Autor
ttk.Label(frame, text="Autor:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
entry_autor = ttk.Entry(frame, width=30)
entry_autor.grid(row=1, column=1, padx=5, pady=5)

# Label e entry para Preço
ttk.Label(frame, text="Preço (ex: 29.90):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
entry_preco = ttk.Entry(frame, width=15)
entry_preco.grid(row=2, column=1, padx=5, pady=5)

# Botão para enviar (salvar) o livro
btn_enviar = ttk.Button(frame, text="Salvar Livro", command=enviar_livro)
btn_enviar.grid(row=3, column=0, columnspan=2, pady=10)

# Label para exibir o resultado
label_result = ttk.Label(frame, text="Resultado: ", font=("Arial", 12))
label_result.grid(row=4, column=0, columnspan=2, pady=10)

# Iniciar o loop da interface
root.mainloop()

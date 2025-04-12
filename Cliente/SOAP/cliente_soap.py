import tkinter as tk
from tkinter import ttk, messagebox
import requests
import xml.etree.ElementTree as ET

# URL do serviço SOAP (assegure-se de que o servidor avançado esteja rodando)
SOAP_URL = "http://127.0.0.1:5000/soap"

def calcular():
    try:
        # Obter os dados da interface
        operacao = operacao_var.get()
        num1_text = entry_num1.get().strip()
        num2_text = entry_num2.get().strip()
        
        # Verificar se os campos não estão vazios
        if not num1_text or not num2_text:
            messagebox.showwarning("Entrada Inválida", "Por favor, insira os dois números.")
            return
        
        # Converter strings para inteiros
        num1 = int(num1_text)
        num2 = int(num2_text)
        
        # Construir a mensagem SOAP (conforme o esquema definido no advanced_schema.xsd)
        soap_request = f"""<?xml version="1.0" encoding="UTF-8"?>
<Envelope>
  <Body>
    <OperacaoRequest>
      <operacao>{operacao}</operacao>
      <numero1>{num1}</numero1>
      <numero2>{num2}</numero2>
    </OperacaoRequest>
  </Body>
</Envelope>"""
        
        headers = {"Content-Type": "text/xml"}
        response = requests.post(SOAP_URL, data=soap_request, headers=headers)
        
        # Processar a resposta: Tenta extrair o elemento <resultado>
        root_resp = ET.fromstring(response.text)
        res_elem = root_resp.find(".//resultado")
        
        if res_elem is not None:
            label_result.config(text=f"Resultado: {res_elem.text}")
        else:
            # Se não encontrou <resultado>, tenta extrair a mensagem de erro do Fault
            fault_elem = root_resp.find(".//faultstring")
            if fault_elem is not None:
                label_result.config(text=f"Erro: {fault_elem.text}")
            else:
                label_result.config(text="Erro: Resposta não reconhecida.")
    except Exception as e:
        label_result.config(text=f"Erro: {str(e)}")

# Criar a janela principal
root = tk.Tk()
root.title("Cliente SOAP - Calculadora")

# Configuração do layout
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Label e entry para Número 1
ttk.Label(frame, text="Número 1:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
entry_num1 = ttk.Entry(frame, width=15)
entry_num1.grid(row=0, column=1, padx=5, pady=5)

# Label e entry para Número 2
ttk.Label(frame, text="Número 2:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
entry_num2 = ttk.Entry(frame, width=15)
entry_num2.grid(row=1, column=1, padx=5, pady=5)

# Combobox para escolher a operação
ttk.Label(frame, text="Operação:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
operacao_var = tk.StringVar()
combo_operacao = ttk.Combobox(frame, textvariable=operacao_var, state="readonly", width=13)
combo_operacao['values'] = ("soma", "subtracao", "multiplicacao", "divisao")
combo_operacao.current(0)  # Seleciona "soma" por padrão
combo_operacao.grid(row=2, column=1, padx=5, pady=5)

# Botão para calcular
btn_calcular = ttk.Button(frame, text="Calcular", command=calcular)
btn_calcular.grid(row=3, column=0, columnspan=2, pady=10)

# Label para exibir o resultado
label_result = ttk.Label(frame, text="Resultado: ", font=("Arial", 12))
label_result.grid(row=4, column=0, columnspan=2, pady=10)

# Ajusta o layout e inicia o loop da interface
root.mainloop()

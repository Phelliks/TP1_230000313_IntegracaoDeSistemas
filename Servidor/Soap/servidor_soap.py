# soap_server.py

import os
import xml.etree.ElementTree as ET
from flask import Flask, request, Response

app = Flask(__name__)

# Base de dados em memória para SOAP (opcional)
livros = []

# Caminho do arquivo XML para persistência
XML_FILE_PATH = os.path.join("Servidor", "Soap", "XML", "livros.xml")

def inicializar_xml():
    """Cria o diretório e o arquivo XML, se ainda não existirem."""
    xml_dir = os.path.dirname(XML_FILE_PATH)
    os.makedirs(xml_dir, exist_ok=True)
    if not os.path.exists(XML_FILE_PATH):
        root = ET.Element("livros")
        tree = ET.ElementTree(root)
        tree.write(XML_FILE_PATH, encoding="utf-8", xml_declaration=True)

def adicionar_livro_xml(nome, autor, preco):
    """Adiciona um livro ao arquivo XML."""
    inicializar_xml()
    tree = ET.parse(XML_FILE_PATH)
    root = tree.getroot()
    livro_elem = ET.Element("livro")
    ET.SubElement(livro_elem, "nome").text = nome
    ET.SubElement(livro_elem, "autor").text = autor
    ET.SubElement(livro_elem, "preco").text = str(preco)
    root.append(livro_elem)
    tree.write(XML_FILE_PATH, encoding="utf-8", xml_declaration=True)

def atualizar_livro_xml(nome, novo_preco):
    """Atualiza o preço de um livro identificado pelo nome no arquivo XML."""
    inicializar_xml()
    tree = ET.parse(XML_FILE_PATH)
    root = tree.getroot()
    updated = False
    for livro in root.findall("livro"):
        if livro.findtext("nome", "").strip().lower() == nome.strip().lower():
            livro.find("preco").text = str(novo_preco)
            updated = True
            break
    if updated:
        tree.write(XML_FILE_PATH, encoding="utf-8", xml_declaration=True)
    return updated

@app.route('/soap', methods=['POST'])
def soap_service():
    xml_request = request.data.decode('utf-8')
    try:
        root_req = ET.fromstring(xml_request)
        body = root_req.find("Body")
        if body is None:
            raise ValueError("Elemento Body não encontrado.")

        # Inserção: <LivroRequest>
        livro_req = body.find("LivroRequest")
        if livro_req is not None:
            nome = livro_req.findtext("nome")
            autor = livro_req.findtext("autor")
            preco_text = livro_req.findtext("preco")
            if not nome or not autor or not preco_text:
                raise ValueError("Campos obrigatórios ausentes para inserção.")
            preco = float(preco_text)
            livros.append({"nome": nome, "autor": autor, "preco": preco})
            adicionar_livro_xml(nome, autor, preco)
            response_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Body>
    <LivroResponse>
      <mensagem>Livro inserido com sucesso!</mensagem>
    </LivroResponse>
  </soapenv:Body>
</soapenv:Envelope>"""
            return Response(response_xml, mimetype="text/xml")

        # Consulta: <LivroConsultaRequest>
        livro_consulta = body.find("LivroConsultaRequest")
        if livro_consulta is not None:
            nome_query = livro_consulta.findtext("nome")
            if not nome_query:
                raise ValueError("Campo 'nome' ausente na consulta.")
            info = None
            for livro in livros:
                if livro.get("nome", "").strip().lower() == nome_query.strip().lower():
                    info = livro
                    break
            if info is None:
                raise ValueError("Livro não encontrado.")
            response_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Body>
    <LivroConsultaResponse>
      <nome>{info.get('nome')}</nome>
      <autor>{info.get('autor')}</autor>
      <preco>{info.get('preco')}</preco>
    </LivroConsultaResponse>
  </soapenv:Body>
</soapenv:Envelope>"""
            return Response(response_xml, mimetype="text/xml")

        # Atualização: <LivroUpdateRequest>
        livro_update = body.find("LivroUpdateRequest")
        if livro_update is not None:
            nome = livro_update.findtext("nome")
            novo_preco_text = livro_update.findtext("preco")
            if not nome or not novo_preco_text:
                raise ValueError("Dados insuficientes para atualização via SOAP.")
            novo_preco = float(novo_preco_text)
            if atualizar_livro_xml(nome, novo_preco):
                response_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Body>
    <LivroUpdateResponse>
      <mensagem>Livro atualizado com sucesso!</mensagem>
    </LivroUpdateResponse>
  </soapenv:Body>
</soapenv:Envelope>"""
                return Response(response_xml, mimetype="text/xml")
            else:
                raise ValueError("Livro não encontrado para atualização.")

        raise ValueError("Operação não reconhecida. Use LivroRequest para inserção, LivroConsultaRequest para consulta ou LivroUpdateRequest para atualização.")
    except Exception as e:
        fault_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Body>
    <soapenv:Fault>
      <faultcode>SOAP-ENV:Client</faultcode>
      <faultstring>{str(e)}</faultstring>
    </soapenv:Fault>
  </soapenv:Body>
</soapenv:Envelope>"""
        return Response(fault_xml, status=400, mimetype="text/xml")

if __name__ == '__main__':
    print("Servidor SOAP rodando em http://127.0.0.1:5000/soap")
    app.run(host="127.0.0.1", port=5000, debug=True)

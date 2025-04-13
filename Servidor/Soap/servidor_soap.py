import os
import xml.etree.ElementTree as ET
from flask import Flask, request, Response

app = Flask(__name__)

# Caminho do arquivo XML para persistência
XML_FILE_PATH = os.path.join("Servidor", "XML", "livros.xml")

def inicializar_xml():
    """Cria o diretório e o arquivo XML, se ainda não existirem."""
    xml_dir = os.path.dirname(XML_FILE_PATH)
    os.makedirs(xml_dir, exist_ok=True)
    if not os.path.exists(XML_FILE_PATH):
        root = ET.Element("livros")
        tree = ET.ElementTree(root)
        tree.write(XML_FILE_PATH, encoding="utf-8", xml_declaration=True)

def atualizar_livro_xml(nome, novo_autor=None, novo_preco=None):
    """
    Atualiza o autor e/ou preço do livro identificado pelo nome no arquivo XML.
    Retorna True se o livro for encontrado.
    """
    inicializar_xml()
    tree = ET.parse(XML_FILE_PATH)
    root = tree.getroot()
    updated = False
    for livro in root.findall("livro"):
        if livro.findtext("nome", "").strip().lower() == nome.strip().lower():
            if novo_autor:
                livro.find("autor").text = novo_autor
            if novo_preco is not None:
                livro.find("preco").text = str(novo_preco)
            updated = True
            break
    if updated:
        tree.write(XML_FILE_PATH, encoding="utf-8", xml_declaration=True)
    return updated

@app.route('/soap', methods=['POST'])
def soap_service():
    """
    Serviço SOAP para modificar livros no XML.
    Utiliza <LivroUpdateRequest> para atualizar autor e/ou preço de um livro.
    """
    xml_request = request.data.decode('utf-8')
    try:
        root_req = ET.fromstring(xml_request)
        body = root_req.find("Body")
        if body is None:
            raise ValueError("Elemento Body não encontrado.")

        # Atualização: <LivroUpdateRequest>
        livro_update = body.find("LivroUpdateRequest")
        if livro_update is not None:
            nome = livro_update.findtext("nome")
            novo_autor = livro_update.findtext("autor")
            novo_preco_text = livro_update.findtext("preco")
            novo_preco = float(novo_preco_text) if novo_preco_text else None
            if not nome or (not novo_autor and novo_preco is None):
                raise ValueError("Dados insuficientes para atualização via SOAP.")
            if atualizar_livro_xml(nome, novo_autor, novo_preco):
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
        else:
            raise ValueError("Operação não reconhecida. Use LivroUpdateRequest para atualizar.")
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
    app.run(port=5000)

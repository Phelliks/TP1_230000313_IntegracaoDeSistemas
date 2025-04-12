from flask import Flask, request, Response
import xmlschema
import xml.etree.ElementTree as ET
import os

app = Flask(__name__)

# Carregar o XSD de validação para a requisição SOAP
REQUEST_XSD_PATH = "Servidor/Soap/book_request_schema.xsd"
try:
    request_xsd = xmlschema.XMLSchema(REQUEST_XSD_PATH)
except Exception as ex:
    print(f"Erro ao carregar o XSD da requisição: {ex}")
    exit(1)

# Caminho do arquivo XML onde os livros serão salvos
XML_FILE = "livros.xml"
# XSD que define a estrutura de persistência (livros)
PERSISTENCE_XSD = "Servidor/Soap/livros_schema.xsd"

# Função para criar o arquivo XML de livros (se não existir)
def inicializar_xml():
    if not os.path.exists(XML_FILE):
        # Cria a raiz com referência ao XSD de persistência
        root = ET.Element("livros", {
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:noNamespaceSchemaLocation": PERSISTENCE_XSD
        })
        tree = ET.ElementTree(root)
        # Escreve com declaração XML
        tree.write(XML_FILE, encoding="utf-8", xml_declaration=True)

# Função para adicionar um livro ao arquivo XML
def adicionar_livro(nome, autor, preco):
    inicializar_xml()
    tree = ET.parse(XML_FILE)
    root = tree.getroot()
    
    livro = ET.Element("livro")
    ET.SubElement(livro, "nome").text = nome
    ET.SubElement(livro, "autor").text = autor
    ET.SubElement(livro, "preco").text = str(preco)
    
    root.append(livro)
    
    tree.write(XML_FILE, encoding="utf-8", xml_declaration=True)

@app.route('/soap', methods=['POST'])
def soap_service():
    xml_request = request.data.decode('utf-8')
    
    try:
        # Valida o XML de requisição usando o XSD
        if not request_xsd.is_valid(xml_request):
            validation_errors = "\n".join([str(err) for err in request_xsd.iter_errors(xml_request)])
            raise ValueError(f"Erro na validação XSD da requisição:\n{validation_errors}")

        # Parse da requisição com ElementTree
        root_req = ET.fromstring(xml_request)
        # Navega até o elemento LivroRequest (considerando que não há namespace)
        livro_req = root_req.find('./Body/LivroRequest')
        if livro_req is None:
            raise ValueError("Elemento LivroRequest não encontrado na requisição.")
        
        nome = livro_req.findtext("nome")
        autor = livro_req.findtext("autor")
        preco_text = livro_req.findtext("preco")
        if nome is None or autor is None or preco_text is None:
            raise ValueError("Campos obrigatórios (nome, autor, preco) ausentes.")
        preco = float(preco_text)

        # Salva o livro no arquivo XML
        adicionar_livro(nome, autor, preco)
        
        # Resposta SOAP de sucesso
        response_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Body>
    <LivroResponse>
      <mensagem>Livro salvo com sucesso!</mensagem>
    </LivroResponse>
  </soapenv:Body>
</soapenv:Envelope>"""
        return Response(response_xml, mimetype='text/xml')

    except Exception as e:
        # Resposta SOAP de erro (Fault)
        fault_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Body>
    <soapenv:Fault>
      <faultcode>SOAP-ENV:Client</faultcode>
      <faultstring>{str(e)}</faultstring>
    </soapenv:Fault>
  </soapenv:Body>
</soapenv:Envelope>"""
        return Response(fault_xml, status=400, mimetype='text/xml')

if __name__ == '__main__':
    print("Servidor SOAP avançado (Livros com XSD) rodando em http://127.0.0.1:5000/soap")
    app.run(host="127.0.0.1", port=5000)

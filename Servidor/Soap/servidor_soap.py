# Importação das bibliotecas necessárias
import os
import xml.etree.ElementTree as ET
from flask import Flask, request, Response

# Inicialização do Flask
app = Flask(__name__)

# Configuração do caminho do arquivo XML
XML_FILE_PATH = "/data/livros.xml"

# Funções auxiliares para manipulação do XML
def inicializar_xml():
    xml_dir = os.path.dirname(XML_FILE_PATH)
    os.makedirs(xml_dir, exist_ok=True)
    if not os.path.exists(XML_FILE_PATH):
        root = ET.Element("livros")
        tree = ET.ElementTree(root)
        tree.write(XML_FILE_PATH, encoding="utf-8", xml_declaration=True)

def atualizar_livro_xml(nome, novo_autor=None, novo_preco=None):

    #Atualiza o autor e/ou preço do livro identificado pelo nome no arquivo XML.
    #Retorna True se o livro for encontrado.

    inicializar_xml()
    tree = ET.parse(XML_FILE_PATH)
    root = tree.getroot()
    updated = False

    # Busca e atualiza o livro
    for livro in root.findall("livro"):
        if livro.findtext("nome", "").strip().lower() == nome.strip().lower():
            if novo_autor:
                livro.find("autor").text = novo_autor
            if novo_preco is not None:
                livro.find("preco").text = str(novo_preco)
            updated = True
            break

    # Salva as alterações se houve atualização
    if updated:
        tree.write(XML_FILE_PATH, encoding="utf-8", xml_declaration=True)
    return updated

# Endpoint SOAP para processamento das requisições
@app.route('/soap', methods=['POST'])
def soap_service():
    xml_request = request.data.decode('utf-8')
    try:
        # Processamento da requisição SOAP
        root_req = ET.fromstring(xml_request)
        body = root_req.find("Body")
        if body is None:
            raise ValueError("Elemento Body não encontrado.")

        # Processamento da atualização do livro
        livro_update = body.find("LivroUpdateRequest")
        if livro_update is not None:
            # Extração dos dados da requisição
            nome = livro_update.findtext("nome")
            novo_autor = livro_update.findtext("autor")
            novo_preco_text = livro_update.findtext("preco")
            novo_preco = float(novo_preco_text) if novo_preco_text else None

            # Validação dos dados
            if not nome or (not novo_autor and novo_preco is None):
                raise ValueError("Dados insuficientes para atualização via SOAP.")

            # Atualização do livro e geração da resposta
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

    # Tratamento de erros e geração da mensagem de falha
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

# Inicialização do servidor
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)

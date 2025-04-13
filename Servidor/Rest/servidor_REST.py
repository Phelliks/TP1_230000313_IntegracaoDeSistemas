import os
import xml.etree.ElementTree as ET
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from jsonschema import validate, ValidationError

app = Flask(__name__)
api = Api(app)

# JSON Schema para validação de livros
book_schema = {
    "type": "object",
    "properties": {
        "nome": {"type": "string"},
        "autor": {"type": "string"},
        "preco": {"type": "number"}
    },
    "required": ["nome", "autor", "preco"]
}

# Caminho do arquivo XML para persistência
XML_FILE_PATH = os.path.join("Servidor", "XML", "livros.xml")

def inicializar_xml():
    """Cria o diretório e o arquivo XML com a raiz <livros> se não existirem."""
    xml_dir = os.path.dirname(XML_FILE_PATH)
    os.makedirs(xml_dir, exist_ok=True)
    if not os.path.exists(XML_FILE_PATH):
        root = ET.Element("livros")
        tree = ET.ElementTree(root)
        tree.write(XML_FILE_PATH, encoding="utf-8", xml_declaration=True)

def adicionar_livro_xml(nome, autor, preco):
    """Adiciona um novo livro ao arquivo XML."""
    inicializar_xml()
    tree = ET.parse(XML_FILE_PATH)
    root = tree.getroot()
    livro_elem = ET.Element("livro")
    ET.SubElement(livro_elem, "nome").text = nome
    ET.SubElement(livro_elem, "autor").text = autor
    ET.SubElement(livro_elem, "preco").text = str(preco)
    root.append(livro_elem)
    tree.write(XML_FILE_PATH, encoding="utf-8", xml_declaration=True)

# Recurso RESTful para inserir livros
class LivroResource(Resource):
    def post(self):
        """
        POST para inserir um novo livro.
        Valida o JSON com JSON Schema e salva no XML.
        """
        try:
            livro = request.json
            validate(instance=livro, schema=book_schema)
            adicionar_livro_xml(livro["nome"], livro["autor"], livro["preco"])
            return {"mensagem": "Livro inserido com sucesso!"}, 201
        except ValidationError as e:
            return {"erro": f"Erro de validação: {e.message}"}, 400
        except Exception as e:
            return {"erro": f"Erro inesperado: {str(e)}"}, 500

api.add_resource(LivroResource, '/REST')

if __name__ == '__main__':
    app.run(port=5000)

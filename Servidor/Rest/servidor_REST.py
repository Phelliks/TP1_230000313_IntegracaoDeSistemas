# rest_server.py

import os
import xml.etree.ElementTree as ET
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from jsonschema import validate, ValidationError
from jsonpath_ng import parse

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

# Base de dados em memória para REST (para retornos rápidos)
livros = []

# Caminho do arquivo XML para persistência compartilhada
XML_FILE_PATH = os.path.join("Servidor", "Soap", "XML", "livros.xml")

def inicializar_xml():
    """Cria o diretório e o arquivo XML com a raiz <livros> se não existirem."""
    xml_dir = os.path.dirname(XML_FILE_PATH)
    os.makedirs(xml_dir, exist_ok=True)
    if not os.path.exists(XML_FILE_PATH):
        root = ET.Element("livros")
        tree = ET.ElementTree(root)
        tree.write(XML_FILE_PATH, encoding="utf-8", xml_declaration=True)

def adicionar_livro_xml(nome, autor, preco):
    """Adiciona um novo livro no arquivo XML."""
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
    """Atualiza o preço de um livro identificado pelo nome no arquivo XML.
       Retorna True se o livro for encontrado."""
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

def atualizar_livro_memoria(nome, novo_preco):
    """Atualiza o livro na base de dados em memória."""
    updated = False
    for book in livros:
        if book.get("nome", "").strip().lower() == nome.strip().lower():
            book["preco"] = novo_preco
            updated = True
    return updated

def atualizar_livro(nome, novo_preco):
    """Realiza a atualização na memória e no XML."""
    mem_updated = atualizar_livro_memoria(nome, novo_preco)
    xml_updated = atualizar_livro_xml(nome, novo_preco)
    return mem_updated or xml_updated

# Recurso RESTful
class LivroResource(Resource):
    def get(self):
        """
        GET para consulta.
        Aceita parâmetro de consulta 'query' para aplicar JSONPath sobre os livros.
        Exemplo: /REST?query=$[?(@.preco>30)]
        """
        query = request.args.get('query')
        if query:
            try:
                expr = parse(query)
                resultados = [match.value for match in expr.find(livros)]
                return jsonify(resultados)
            except Exception as e:
                return {"erro": f"Consulta JSONPath inválida: {str(e)}"}, 400
        return jsonify(livros)

    def post(self):
        """
        POST para inserir um novo livro.
        O JSON recebido é validado com JSON Schema, salvo na memória e persistido no XML.
        """
        try:
            livro = request.json
            validate(instance=livro, schema=book_schema)
            livros.append(livro)
            adicionar_livro_xml(livro["nome"], livro["autor"], livro["preco"])
            return {"mensagem": "Livro inserido com sucesso!"}, 201
        except ValidationError as e:
            return {"erro": f"Erro de validação: {e.message}"}, 400
        except Exception as e:
            return {"erro": f"Erro inesperado: {str(e)}"}, 500

    def put(self):
        """
        PUT para atualizar o preço de um livro.
        Espera um JSON com 'nome' e 'preco'.
        """
        try:
            data = request.json
            nome = data.get("nome")
            novo_preco = data.get("preco")
            if not nome or novo_preco is None:
                return {"erro": "Dados insuficientes para atualização. Informe 'nome' e 'preco'."}, 400
            if atualizar_livro(nome, novo_preco):
                return {"mensagem": "Livro atualizado com sucesso!"}, 200
            else:
                return {"erro": "Livro não encontrado."}, 404
        except Exception as e:
            return {"erro": f"Erro inesperado: {str(e)}"}, 500

api.add_resource(LivroResource, '/REST')

if __name__ == '__main__':
    print("Servidor REST rodando em http://127.0.0.1:5001/REST")
    app.run(host="127.0.0.1", port=5001, debug=True)

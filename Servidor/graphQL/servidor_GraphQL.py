import xml.etree.ElementTree as ET
from flask import Flask
from flask_graphql import GraphQLView
import graphene

CAMINHO_XML = "/data/livros.xml"

class Resultado(graphene.ObjectType):
    sucesso = graphene.Boolean()
    mensagem = graphene.String()

class EliminarLivro(graphene.Mutation):
    class Arguments:
        nome = graphene.String(required=True)

    Output = Resultado

    def mutate(root, info, nome):
        try:
            tree = ET.parse(CAMINHO_XML)
            root_xml = tree.getroot()
            livros = root_xml.findall("livro")

            encontrados = 0
            for livro in livros:
                if livro.find("nome").text.strip().lower() == nome.strip().lower():
                    root_xml.remove(livro)
                    encontrados += 1

            if encontrados > 0:
                tree.write(CAMINHO_XML, encoding="utf-8", xml_declaration=True)
                return Resultado(sucesso=True, mensagem=f"{encontrados} livro(s) removido(s).")
            else:
                return Resultado(sucesso=False, mensagem="Livro não encontrado.")

        except Exception as e:
            return Resultado(sucesso=False, mensagem=f"Erro: {str(e)}")

class Mutation(graphene.ObjectType):
    eliminar_livro = EliminarLivro.Field()

schema = graphene.Schema(mutation=Mutation)

app = Flask(__name__)
app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view(
        "graphql",
        schema=schema,
        graphiql=True  # Para usar interface no browser
    ),
)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000)

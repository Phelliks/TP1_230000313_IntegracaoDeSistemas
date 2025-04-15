# Importação das bibliotecas necessárias
import xml.etree.ElementTree as ET  # Para manipulação de arquivos XML
from flask import Flask  # Framework web
from flask_graphql import GraphQLView  # Integração GraphQL com Flask
import graphene  # Framework GraphQL para Python

# Configuração do caminho do arquivo XML
CAMINHO_XML = "/data/livros.xml"

# Definição do tipo de objeto para retorno das operações
class Resultado(graphene.ObjectType):
    sucesso = graphene.Boolean()  # Indica se a operação foi bem-sucedida
    mensagem = graphene.String()   # Mensagem descritiva do resultado

# Definição da mutação para eliminar livros
class EliminarLivro(graphene.Mutation):
    class Arguments:
        nome = graphene.String(required=True)  # Argumento obrigatório para o nome do livro

    Output = Resultado  # Tipo de retorno da mutação

    def mutate(root, info, nome):
        try:
            # Carrega e processa o XML para mexer nos livros
            tree = ET.parse(CAMINHO_XML)
            root_xml = tree.getroot()
            livros = root_xml.findall("livro")

            # Procura e remove livros com o nome especificado
            encontrados = 0
            for livro in livros:
                if livro.find("nome").text.strip().lower() == nome.strip().lower():
                    root_xml.remove(livro)
                    encontrados += 1

            # Salva as alterações e retorna o resultado
            if encontrados > 0:
                tree.write(CAMINHO_XML, encoding="utf-8", xml_declaration=True)
                return Resultado(sucesso=True, mensagem=f"{encontrados} livro(s) removido(s).")
            else:
                return Resultado(sucesso=False, mensagem="Livro não encontrado.")

        except Exception as e:
            return Resultado(sucesso=False, mensagem=f"Erro: {str(e)}")

# Configuração do schema GraphQL
class Mutation(graphene.ObjectType):
    eliminar_livro = EliminarLivro.Field()  # Registro da mutação

schema = graphene.Schema(mutation=Mutation)

# Configuração do servidor Flask e endpoint GraphQL
app = Flask(__name__)
app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view(
        "graphql",
        schema=schema,
        graphiql=True  # Habilita interface gráfica para testes
    ),
)

# Inicialização do servidor
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000)  # Servidor disponível em todas as interfaces na porta 4000

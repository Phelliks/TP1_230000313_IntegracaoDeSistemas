# Importação das bibliotecas necessárias
from concurrent import futures
import grpc
import livro_pb2
import livro_pb2_grpc
import xml.etree.ElementTree as ET

# Definição do serviço gRPC para gerenciamento de livros
class LivroServiceServicer(livro_pb2_grpc.LivroServiceServicer):
    # Implementação do método de procura de livros
    def ProcurarLivro(self, request, context):
        nome_procurado = request.nome.strip().lower()

        try:
            # Carrega e processa o XML para mexer nos livros
            tree = ET.parse("/data/livros.xml")
            root = tree.getroot()

            # Procura o livro pelo nome
            for livro in root.findall("livro"):
                nome = livro.find("nome").text.strip()
                if nome.lower() == nome_procurado:
                    autor = livro.find("autor").text.strip()
                    preco = float(livro.find("preco").text.strip())
                    return livro_pb2.LivroResponse(nome=nome, autor=autor, preco=preco)

            # Retorna erro se o livro não for encontrado
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Livro não encontrado.")
            return livro_pb2.LivroResponse()

        except Exception as e:
            # Tratamento de erros durante a leitura do XML
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Erro ao ler o XML: {str(e)}")
            return livro_pb2.LivroResponse()

# Configuração e inicialização do servidor gRPC
def servir():
    # Cria o servidor com um pool de threads
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Registra o serviço no servidor
    livro_pb2_grpc.add_LivroServiceServicer_to_server(LivroServiceServicer(), server)
    # Configura a porta de escuta
    server.add_insecure_port('[::]:50051')
    # Inicia o servidor e aguarda
    server.start()
    server.wait_for_termination()

# Ponto de entrada do programa
if __name__ == "__main__":
    servir()

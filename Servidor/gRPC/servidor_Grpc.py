from concurrent import futures
import grpc
import livro_pb2
import livro_pb2_grpc
import xml.etree.ElementTree as ET

class LivroServiceServicer(livro_pb2_grpc.LivroServiceServicer):
    def ProcurarLivro(self, request, context):
        nome_procurado = request.nome.strip().lower()

        try:
            tree = ET.parse("/data/livros.xml")
            root = tree.getroot()

            for livro in root.findall("livro"):
                nome = livro.find("nome").text.strip()
                if nome.lower() == nome_procurado:
                    autor = livro.find("autor").text.strip()
                    preco = float(livro.find("preco").text.strip())
                    return livro_pb2.LivroResponse(nome=nome, autor=autor, preco=preco)

            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Livro não encontrado.")
            return livro_pb2.LivroResponse()

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Erro ao ler o XML: {str(e)}")
            return livro_pb2.LivroResponse()

def servir():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    livro_pb2_grpc.add_LivroServiceServicer_to_server(LivroServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    servir()

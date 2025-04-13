from concurrent import futures
import grpc
import time

import books_pb2
import books_pb2_grpc

# Simulação de "base de dados" de livros. 
# Em uma implementação real, você poderia ler do arquivo XML que os outros serviços atualizam.
BOOKS = [
    books_pb2.BookResponse(nome="O Alquimista", autor="Paulo Coelho", preco=29.90),
    books_pb2.BookResponse(nome="Dom Casmurro", autor="Machado de Assis", preco=45.0)
]

class BookServiceServicer(books_pb2_grpc.BookServiceServicer):
    def GetBook(self, request, context):
        # Busca o livro pela correspondência do nome (case insensitive)
        for book in BOOKS:
            if book.nome.lower() == request.nome.lower():
                return book
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("Livro não encontrado")
        return books_pb2.BookResponse()

    def ListBooks(self, request, context):
        # Método de streaming: envia todos os livros
        for book in BOOKS:
            yield book

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    books_pb2_grpc.add_BookServiceServicer_to_server(BookServiceServicer(), server)
    server.add_insecure_port('[::]:50053')
    server.start()
    print("gRPC Server rodando na porta 50053")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()

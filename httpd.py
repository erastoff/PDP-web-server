# import datetime
# import logging
# from http.server import BaseHTTPRequestHandler, HTTPServer
# from urllib.parse import urlparse, parse_qs
#
#
# # Создаем собственный класс обработчика запросов
# class SimpleRequestHandler(BaseHTTPRequestHandler):
#     def do_GET(self):
#         parsed_url = urlparse(self.path)
#         params = parse_qs(parsed_url.query)
#         name_param = params.get("name", [""])[0] or "unnamed user"
#
#         response_content = f"Hello, {name_param}. This is a simple web server!"
#         current_datetime = datetime.datetime.now()
#         # Отправляем успешный ответ
#         self.send_response(200)
#         # Устанавливаем заголовок Content-type
#         self.send_header("Date", str(current_datetime))
#         if "Server" in self.headers:
#             del self.headers["Server"]
#         self.send_header("Server", "MyWebServer")
#         self.send_header("Content-Type", "text/html")
#
#         # Устанавливаем заголовок Content-Length
#         self.send_header("Content-Length", str(len(response_content)))
#         # Завершаем заголовки
#         self.end_headers()
#         print(self.headers)
#
#         # Отправляем тело ответа
#         self.wfile.write(response_content.encode("utf-8"))
#
#     def do_HEAD(self):
#         # parsed_url = urlparse(self.path)
#         # params = parse_qs(parsed_url.query)
#         # name_param = params.get("name", [""])[0]
#         # Отправляем успешный ответ
#         self.send_response(200)
#         # Устанавливаем заголовок Content-type
#         self.send_header("Content-type", "text/html")
#         # Завершаем заголовки
#         self.end_headers()
#         # Отправляем тело ответа
#         # response_content = f"Hello, {name_param}! This is a simple web server."
#         # self.wfile.write(response_content.encode("utf-8"))
#
#
# # Устанавливаем порт, на котором будет работать сервер
# port = 8000
#
# # Создаем экземпляр HTTP-сервера с нашим обработчиком запросов
# httpd = HTTPServer(("", port), SimpleRequestHandler)
#
# # Выводим сообщение о запуске сервера
# print(f"Server running, port: {port}")
#
# # Запускаем сервер и ждем запросов
# httpd.serve_forever()
#
#
# if __name__ == "__main__":
#     logging.basicConfig(
#         filename=args.log,
#         level=logging.INFO,
#         format="[%(asctime)s] %(levelname).1s %(message)s",
#         datefmt="%Y.%m.%d %H:%M:%S",
#     )
#     # Устанавливаем порт, на котором будет работать сервер
#     port = 8000
#
#     # Создаем экземпляр HTTP-сервера с нашим обработчиком запросов
#     httpd = HTTPServer(("", port), SimpleRequestHandler)
#
#     # Выводим сообщение о запуске сервера
#     print(f"Server running, port: {port}")
#
#     # Запускаем сервер и ждем запросов
#     httpd.serve_forever()

import logging
import socket
import time


class SimpleServer:
    def __init__(self, host="localhost", port=8000):
        self.host = host
        self.port = port

    def handle_request(self, client_socket):
        # Читаем данные из клиента
        request_data = client_socket.recv(1024).decode("utf-8")

        # Печатаем запрос (для отладки)
        print("Received request:")
        print(request_data)
        logging.info("Received request:/n" + request_data)

        # Отправляем ответ
        # response = "HTTP/1.1 200 OK\nContent-Type: text/html\n\nHello, this is a simple web server!"
        # client_socket.sendall(response.encode("utf-8"))

        # Извлекаем имя из запроса (пример: /?name=John)
        name = ""
        if "GET /?name=" in request_data:
            start_index = request_data.find("GET /?name=") + len("GET /?name=")
            end_index = request_data.find(" HTTP/1.1")
            name = request_data[start_index:end_index]

        # Формируем ответ
        response_body = f"Hello, {name}! This is a simple web server."
        response_headers = (
            "HTTP/1.1 200 OK\n"
            f"Date: {time.strftime('%a, %d %b %Y %H:%M:%S GMT')}\n"
            "Server: MyCustomServer\n"
            f"Content-Length: {len(response_body)}\n"
            "Content-Type: text/html\n"
            "Connection: close\n\n"
        )

        # Отправляем ответ
        client_socket.sendall((response_headers + response_body).encode("utf-8"))

    def run_server(self):
        # Создаем сокет
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Привязываем сокет к адресу и порту
        server_socket.bind((self.host, self.port))

        # Начинаем прослушивание
        server_socket.listen(5)
        print("Server listening on port 8000...")
        logging.info("Server listening on port 8000...")

        try:
            while True:
                # Принимаем соединение
                client_socket, client_address = server_socket.accept()
                # print(f"Connection from {client_address}")
                logging.info(f"Connection from {client_address}")

                # Обрабатываем запрос
                self.handle_request(client_socket)

                # Закрываем соединение
                client_socket.close()
        except KeyboardInterrupt:
            print("Server shutting down...")
            logging.info("Server shutting down...")
        finally:
            # Закрываем серверный сокет
            server_socket.close()


if __name__ == "__main__":
    logging.basicConfig(
        filename="log",
        level=logging.INFO,
        format="[%(asctime)s] %(levelname).1s %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
    )

    simple_server = SimpleServer()
    simple_server.run_server()

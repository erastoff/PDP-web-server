import logging
import socket
import time


class SimpleServer:
    def __init__(self, host="localhost", port=8000):
        self.host = host
        self.port = port

    def handle_request(self, client_socket):
        request_data = client_socket.recv(1024).decode("utf-8")

        print("Received request:")
        print(request_data)
        logging.info("Received request:/n" + request_data)

        name = ""
        if "GET /?name=" in request_data:
            start_index = request_data.find("GET /?name=") + len("GET /?name=")
            end_index = request_data.find(" HTTP/1.1")
            name = request_data[start_index:end_index]

        response_body = f"Hello, {name}! This is a simple web server."
        response_headers = (
            "HTTP/1.1 200 OK\n"
            f"Date: {time.strftime('%a, %d %b %Y %H:%M:%S GMT')}\n"
            "Server: MyCustomServer\n"
            f"Content-Length: {len(response_body)}\n"
            "Content-Type: text/html\n"
            "Connection: close\n\n"
        )

        client_socket.sendall((response_headers + response_body).encode("utf-8"))

    def run_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_socket.bind((self.host, self.port))

        server_socket.listen(5)
        print("Server listening on port 8000...")
        logging.info("Server listening on port 8000...")

        try:
            while True:
                client_socket, client_address = server_socket.accept()

                logging.info(f"Connection from {client_address}")

                self.handle_request(client_socket)

                client_socket.close()
        except KeyboardInterrupt:
            print("Server shutting down...")
            logging.info("Server shutting down...")
        finally:
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

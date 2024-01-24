import logging
import socket
import threading
import time

CONTENT_TYPES = (".html", ".css", ".js", ".jpg", ".jpeg", ".png", ".gif", ".swf")
OK = "200 OK"
BAD_REQUEST = "400 BAD_REQUEST"
FORBIDDEN = "403 FORBIDDEN"
NOT_FOUND = "404 NOT_FOUND"
INVALID_REQUEST = "405 METHOD_NOT_ALLOWED"
DOCUMENT_ROOT = "doc/"


class SimpleServer:
    def __init__(self, host="localhost", port=8000):
        self.host = host
        self.port = port

    @staticmethod
    def content_type(request_data):
        for item in CONTENT_TYPES:
            if item in request_data:
                if item in (".html", ".css", ".js"):
                    return f"text/{item.strip('.')}"
                if item in (".png", ".gif", ".swf"):
                    return f"image/{item.strip('.')}"
                if item in (".jpg", ".jpeg"):
                    return "image/jpeg"
        return "text/html"

    @staticmethod
    def create_response_headers(
        code, server="OTUServer", cl=0, ct="text/html", conn="keep-alive"
    ):
        response_headers = (
            f"HTTP/1.1 {code}\n"
            f"Date: {time.strftime('%a, %d %b %Y %H:%M:%S GMT')}\n"
            f"Server: {server}\n"
            f"Content-Length: {cl}\n"
            f"Content-Type: {ct}\n"
            f"Connection: {conn}\n\n"
        )
        return response_headers

    def do_GET(self, request_data):
        logging.info("GET-request accepted")
        content_type = self.content_type(request_data)
        print("CONTENT TYPE: ", content_type)
        try:
            name = "unnamed user"
            if "GET /?name=" in request_data:
                start_index = request_data.find("GET /?name=") + len("GET /?name=")
                end_index = request_data.find(" HTTP/1.1")
                name = request_data[start_index:end_index]
            response_body = f"Hello, {name}! This is a simple web server."
            code = OK
            cl = len(response_body)
            ct = content_type
        except Exception:
            code = NOT_FOUND
            cl = 0
            ct = content_type
            response_body = ""

        response_headers = self.create_response_headers(code=code, cl=cl, ct=ct)
        # response_headers = (
        #     f"HTTP/1.1 200 OK\n"
        #     f"Date: {time.strftime('%a, %d %b %Y %H:%M:%S GMT')}\n"
        #     "Server: SimpleServer\n"
        #     f"Content-Length: {len(response_body)}\n"
        #     "Content-Type: text/html\n"
        #     "Connection: keep-alive\n\n"
        # )
        print("Response response (GET): ")
        print(response_headers, response_body)
        return response_headers, response_body

    def do_HEAD(self, request_data):
        logging.info("HEAD-request accepted")
        content_type = self.content_type(request_data)
        try:
            name = "unnamed user"
            if "Head /?name=" in request_data:
                start_index = request_data.find("GET /?name=") + len("GET /?name=")
                end_index = request_data.find(" HTTP/1.1")
                name = request_data[start_index:end_index]
            response_body = f"Hello, {name}! This is a simple web server."
            code = OK
            cl = len(response_body)
            ct = content_type
        except Exception:
            code = NOT_FOUND
            cl = 0
            ct = content_type
        response_headers = self.create_response_headers(code=code, cl=cl, ct=ct)
        print("Response response (HEAD): ")
        print(response_headers)
        return response_headers, ""

    def handle_request(self, client_socket):
        request_data = client_socket.recv(1024).decode("utf-8")

        print("Received request:")
        print(request_data)
        logging.info("Received request: " + request_data)

        if request_data[:3] == "GET":
            response_headers, response_body = self.do_GET(request_data)
        elif request_data[:4] == "HEAD":
            response_headers, response_body = self.do_HEAD(request_data)
        else:
            logging.info("An unsupported request was received")
            response_headers = (
                "HTTP/1.1 405 NOT_ALLOWED\n"
                f"Date: {time.strftime('%a, %d %b %Y %H:%M:%S GMT')}\n"
                "Server: SimpleServer\n"
                f"Content-Length: 0\n"
                "Content-Type: text/html\n"
                "Connection: keep-alive\n\n"
            )
            print("Response headers (unsupported request): ")
            print(response_headers)
            return

        client_socket.sendall((response_headers + response_body).encode("utf-8"))

    def serve_forever(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server_socket.bind((self.host, self.port))

        server_socket.listen(5)
        print("Server listening on port 8000...")
        logging.info("Server listening on port 8000...")

        try:
            while True:
                client_socket, client_address = server_socket.accept()

                logging.info(f"Connection from {client_address}")

                # self.handle_request(client_socket)
                client_thread = threading.Thread(
                    target=self.handle_request, args=(client_socket,)
                )
                client_thread.start()

                # client_socket.close()
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
    simple_server.serve_forever()

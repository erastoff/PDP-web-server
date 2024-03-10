import argparse
import concurrent.futures
import logging
import os
import socket
import threading
import time
from functools import lru_cache
from urllib.parse import unquote, parse_qs, urlparse

CONTENT_TYPES = (".html", ".css", ".js", ".jpg", ".jpeg", ".png", ".gif", ".swf")
OK = "200 OK"
BAD_REQUEST = "400 BAD_REQUEST"
FORBIDDEN = "403 FORBIDDEN"
NOT_FOUND = "404 NOT_FOUND"
INVALID_REQUEST = "405 METHOD_NOT_ALLOWED"
DOCUMENT_ROOT = "doc/"
N_WORKERS = 4


class Request:
    def __init__(
        self,
        method,
        target,
        version,
        headers,
        rfile,
        server_socket=None,
    ):
        self.method = method
        self.target = target
        self.version = version
        self.headers = headers
        self.rfile = rfile
        self.server_socket = server_socket

        @property
        def path(self):
            return self.url.path

        @property
        @lru_cache(maxsize=None)
        def query(self):
            return parse_qs(self.url.query)

        @property
        @lru_cache(maxsize=None)
        def url(self):
            return urlparse(self.target)


class Response:
    def __init__(self, status, reason, headers=None, body=None):
        self.status = status
        self.reason = reason
        self.headers = headers
        self.body = body

    def headers_to_dict(self):
        response_headers_dict = {}
        for line in self.headers.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                response_headers_dict[key] = value
        # print(response_headers_dict)
        return response_headers_dict

    def read(self):
        return self.body

    def getheader(self, header):
        if self.headers:
            headers = self.headers_to_dict()
            return headers.get(header)
        else:
            return None


class OTUServer:
    def __init__(
        self,
        host="localhost",
        port=8000,
        workers=N_WORKERS,
        worker_threads=[],
    ):
        self.host = host
        self.port = port
        self.workers = workers
        self.server_socket = None
        self.running = False
        self.shutdown_event = threading.Event()
        self.worker_threads = worker_threads

    @staticmethod
    def content_type(request_data):
        for item in CONTENT_TYPES:
            if item in request_data:
                if item in (".html", ".css", "txt"):
                    return f"text/{item.strip('.')}"
                if item in (".png", ".gif"):
                    return f"image/{item.strip('.')}"
                if item in (".jpg", ".jpeg"):
                    return "image/jpeg"
                if item == ".js":
                    return "application/javascript"
                if item == ".swf":
                    return "application/x-shockwave-flash"
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

        return response_headers.encode()

    def do_GET(self, request_data):
        logging.info("GET-request accepted")

        # Fetch path from request (example: /httptest/filename)
        path_param = ""
        if "GET /" in request_data:
            start_index = request_data.find("GET /") + len("GET ")
            end_index = request_data.find(" HTTP/1.1")
            path_param = request_data[start_index:end_index]

        # Full file path
        file_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), unquote(path_param)
        ).lstrip("/")
        file_path = DOCUMENT_ROOT + file_path

        if os.path.exists(file_path):  # and os.path.isfile(file_path):
            if not os.path.isfile(file_path):
                file_path = file_path + "index.html"
            if not os.path.isfile(file_path):
                response_headers = self.create_response_headers(
                    code=NOT_FOUND, cl=0, ct="text/html"
                )
                response = Response(
                    NOT_FOUND.split()[0],
                    NOT_FOUND.split()[1],
                    headers=response_headers,
                    body=b"",
                )
                # return response.headers, ""
                return response
            with open(file_path, "rb") as file:
                file_content = file.read()
                # file_name = file_path.split("/")[-1]
                # new_file_path = DOCUMENT_ROOT + "/" + file_name
                content_type = self.content_type(file_path)
                response_headers = self.create_response_headers(
                    code=OK, cl=len(file_content), ct=content_type
                )
                response = Response(
                    OK.split()[0],
                    OK.split()[1],
                    headers=response_headers,
                    body=file_content,
                )
                # with open(new_file_path, "w") as new_file:
                #     new_file.write(file_content.decode("utf-8"))
                return response
        else:
            # If file doesn't exist
            response_headers = self.create_response_headers(
                code=NOT_FOUND, cl=0, ct="text/html"
            )
            response = Response(
                NOT_FOUND.split()[0],
                NOT_FOUND.split()[1],
                headers=response_headers,
                body=b"",
            )
            return response

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
        response = Response(
            code.split()[0],
            code.split()[1],
            headers=response_headers,
            body=b"",
        )
        print("Response response (HEAD): \n")
        print(response.headers.decode("utf-8"))
        return response

    def handle_request(self, client_socket):
        request_data = client_socket.recv(1024).decode("utf-8")
        print("Received request:")
        print(request_data)
        logging.info("Received request: " + request_data)
        # while not self.shutdown_event.is_set():
        if request_data[:3] == "GET":
            response = self.do_GET(request_data)
        elif request_data[:4] == "HEAD":
            response = self.do_HEAD(request_data)
        else:
            logging.info("An unsupported request was received")
            # Rebuild
            response_headers = self.create_response_headers(
                code=INVALID_REQUEST, cl=0, ct="text/html"
            )
            # response_headers = (
            #     "HTTP/1.1 405 NOT_ALLOWED\n"
            #     f"Date: {time.strftime('%a, %d %b %Y %H:%M:%S GMT')}\n"
            #     "Server: SimpleServer\n"
            #     f"Content-Length: 0\n"
            #     "Content-Type: text/html\n"
            #     "Connection: keep-alive\n\n"
            # )
            # response_body = ""
            response = Response(
                INVALID_REQUEST.split()[0],
                INVALID_REQUEST.split()[1],
                headers=response_headers,
                body=b"",
            )
        print("Response:")
        print(response.headers.decode("utf-8"))
        # client_socket.sendall((response.headers + response.body).encode("utf-8"))
        client_socket.sendall(response.headers + response.body)
        client_socket.close()

    def serve_forever(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(20)
        self.running = True

        print(f"Server listening on port {self.port}...\n")
        logging.info(f"Server listening on port {self.port}...")

        # List to hold references to worker threads
        self.worker_threads = []

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.workers
        ) as executor:
            try:
                while self.running:
                    client_socket, client_address = self.server_socket.accept()
                    # Run request processing in threads pool
                    worker_thread = executor.submit(self.handle_request, client_socket)
                    self.worker_threads.append(worker_thread)

            except KeyboardInterrupt:
                print("Server shutting down...")
                self.shutdown()
                concurrent.futures.wait(self.worker_threads)

            finally:
                if self.server_socket:
                    self.server_socket.close()

    # def request(self, method, path):
    #     request = f"{method} {path} HTTP/1.1\r\nHost: {self.host}:{self.port}\r\n\r\n"
    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    #         client_socket.connect((self.host, self.port))
    #         client_socket.sendall(request.encode())
    #         # response = client_socket.recv(4096).decode()
    #         # return response
    #
    # def getresponse(self):
    #     client_socket, _ = self.server_socket.accept()
    #     request_data = client_socket.recv(1024).decode("utf-8")
    #     response_headers, response_body = self.handle_request(request_data)
    #     response = response_headers + response_body
    #     client_socket.sendall(response.encode("utf-8"))
    #     client_socket.close()

    def shutdown(self):
        self.running = False
        # Closing server's socket
        if self.server_socket:
            self.server_socket.close()
        # self.shutdown_event.set()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-w", "--workers", help="Number of workers", type=int, default=None
    )
    parser.add_argument(
        "-r", "--root", help="Document root folder", default=DOCUMENT_ROOT
    )
    args = parser.parse_args()
    N_WORKERS = args.workers or N_WORKERS
    DOCUMENT_ROOT = args.root or DOCUMENT_ROOT

    logging.basicConfig(
        filename="log",
        level=logging.INFO,
        format="[%(asctime)s] %(levelname).1s %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
    )

    simple_server = OTUServer(host="localhost", port=8000, workers=N_WORKERS)
    simple_server.serve_forever()

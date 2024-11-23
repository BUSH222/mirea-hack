import socket


def send_command(command, host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    client_socket.sendall(command.encode('utf-8'))
    response = client_socket.recv(4096)
    print(f"Ответ от сервера:\n{response.decode('utf-8')}")
    client_socket.close()
    return response

import socket
import ssl


def send_command_tls(command, host, port, certfile=None, keyfile=None):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    context = ssl.create_default_context()

    if certfile and keyfile:
        context.load_cert_chain(certfile=certfile, keyfile=keyfile)

    with context.wrap_socket(client_socket, server_hostname=host) as ssl_socket:
        ssl_socket.connect((host, port))
        ssl_socket.sendall(command.encode('utf-8'))
        response = ssl_socket.recv(4096)
        print(f"Ответ от сервера:\n{response.decode('utf-8')}")

    return response

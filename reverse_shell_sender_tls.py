import socket
import ssl

def send_command(port, ip, command, certfile, keyfile):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind((str(ip), port))
    serverSocket.listen(1)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=certfile, keyfile=keyfile)

    
    connectionSocket, addr = serverSocket.accept()
    connectionSocket = context.wrap_socket(connectionSocket, server_side=True)

    message = connectionSocket.recv(1024)
    print(message.decode())
    connectionSocket.send(command.encode())
    message = connectionSocket.recv(1024).decode()
    print(message)

    connectionSocket.shutdown(socket.SHUT_RDWR)
    connectionSocket.close()
    return message
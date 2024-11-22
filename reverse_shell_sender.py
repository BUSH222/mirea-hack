from socket import *
def send_command(port,ip,command):
    serverSocket = socket(AF_INET,SOCK_STREAM)
    serverSocket.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    serverSocket.bind((str(ip),port))
    serverSocket.listen(1)
    connectionSocket,addr = serverSocket.accept()
    message =connectionSocket.recv(1024)
    print(message)
    connectionSocket.send(command.encode())
    message = connectionSocket.recv(1024).decode()
    print(message)
    connectionSocket.shutdown(SHUT_RDWR)
    connectionSocket.close()
    return message
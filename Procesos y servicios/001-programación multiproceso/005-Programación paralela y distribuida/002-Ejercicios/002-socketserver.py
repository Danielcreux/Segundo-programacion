import socket
import json

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('127.0.0.1', 12348))
server_socket.listen(1)

print("Server is listening on port 12347...")

conn, addr = server_socket.accept()
print(f"Connected by {addr}")

diccionario = {
    "numero": "1.000004",
    "veces": "10000000"
}

while True:
    data = conn.recv(1024)
    if not data:
        break
    print("Received from client:", data.decode())
    
    # ✅ convertir a JSON y luego a bytes
    mensaje = json.dumps(diccionario).encode()
    conn.sendall(mensaje)

conn.close()
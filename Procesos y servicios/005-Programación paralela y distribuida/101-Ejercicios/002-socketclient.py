import socket

HOST = 'localhost'
PORT = 12345

# Conectar al servidor
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

print("Conectado al servidor. Escribe 'quit' para salir")

while True:
    mensaje = input("Tú: ")
    
    if mensaje.lower() == 'quit':
        break
    
    # Enviar mensaje al servidor
    client_socket.send(mensaje.encode('utf-8'))
    
    # Recibir respuesta
    respuesta = client_socket.recv(1024).decode('utf-8')
    print(f"Servidor: {respuesta}")

client_socket.close()

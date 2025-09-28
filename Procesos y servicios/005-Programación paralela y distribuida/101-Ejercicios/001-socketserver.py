import socket

# Configuración del servidor
HOST = 'localhost'  # Escuchar en todas las interfaces
PORT = 12345        # Puerto arbitrario

# Crear socket TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

print(f"Servidor escuchando en {HOST}:{PORT}")
print("Esperando conexiones...")

while True:
    # Aceptar conexión entrante
    client_socket, client_address = server_socket.accept()
    print(f"Conexión establecida con {client_address}")
    
    # Manejar la comunicación con el cliente
    with client_socket:
        while True:
            # Recibir datos del cliente
            data = client_socket.recv(1024)
            if not data:
                break
            
            mensaje = data.decode('utf-8')
            print(f"Cliente dice: {mensaje}")
            
            # Enviar respuesta
            respuesta = f"Servidor recibió: {mensaje}"
            client_socket.send(respuesta.encode('utf-8'))
    
    print(f"Conexión cerrada con {client_address}")
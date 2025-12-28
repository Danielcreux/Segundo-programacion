# client.py
import socket

HOST = "127.0.0.1"   # Server address
PORT = 5000          # Same port as server

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        message = "Hello, server"
        client.sendall(message.encode("utf-8"))

        data = client.recv(1024)
        print("Server responded:", data.decode("utf-8"))

if __name__ == "__main__":
    main()


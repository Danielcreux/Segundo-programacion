# server.py
import socket

HOST = "127.0.0.1"   # Localhost
PORT = 5000          # Any free port

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(1)
        print(f"Server listening on {HOST}:{PORT}")

        conn, addr = server.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print("Received:", data.decode("utf-8"))
                conn.sendall(b"Message received")

if __name__ == "__main__":
    main()


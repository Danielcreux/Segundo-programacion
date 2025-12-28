#!/usr/bin/env python3
import socket
import threading
import sys

HOST = "127.0.0.1"  # Cambia a la IP del servidor si es remoto
PORT = 5000

# Códigos ANSI
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

FG_CYAN = "\033[36m"
FG_GREEN = "\033[32m"
FG_YELLOW = "\033[33m"
FG_RED = "\033[31m"
FG_MAGENTA = "\033[35m"


def imprimir_banner():
    banner = f"""
{FG_CYAN}{BOLD}╔═══════════════════════════════════════════════╗
║                💬  CLIENTE DE CHAT PYTHON       ║
║         Escribe /salir para abandonar el chat   ║
╚═══════════════════════════════════════════════╝{RESET}
"""
    print(banner)


def hilo_receptor(sock: socket.socket) -> None:
    """Hilo que recibe mensajes del servidor y los imprime."""
    try:
        while True:
            datos = sock.recv(1024)
            if not datos:
                print(f"\n{FG_RED}[El servidor se ha desconectado]{RESET}")
                break

            texto = datos.decode("utf-8", errors="ignore")

            # Limpia línea actual y muestra el mensaje
            sys.stdout.write("\r" + " " * 80 + "\r")
            sys.stdout.write(texto)
            sys.stdout.flush()

            # Reponer el prompt
            sys.stdout.write(f"{FG_GREEN}> {RESET}")
            sys.stdout.flush()
    except OSError:
        pass
    finally:
        try:
            sock.close()
        except OSError:
            pass
        salida_segura()


def salida_segura():
    """Salir del proceso desde cualquier hilo."""
    try:
        sys.exit(0)
    except SystemExit:
        import os
        os._exit(0)


def main():
    imprimir_banner()
    apodo = input(f"{FG_YELLOW}Elige un apodo: {RESET}").strip()
    if not apodo:
        apodo = "Anónimo"

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
    except OSError as e:
        print(f"{FG_RED}No se pudo conectar a {HOST}:{PORT} → {e}{RESET}")
        return

    receptor = threading.Thread(target=hilo_receptor, args=(sock,), daemon=True)
    receptor.start()

    sock.sendall((apodo + "\n").encode("utf-8"))

    print(f"{FG_GREEN}Conectado. Escribe tus mensajes. /salir para salir.{RESET}")
    try:
        while True:
            msg = input(f"{FG_GREEN}> {RESET}")
            if msg.strip().lower() == "/salir":
                sock.sendall("/salir".encode("utf-8"))
                break
            try:
                sock.sendall(msg.encode("utf-8"))
            except OSError:
                print(f"{FG_RED}Conexión perdida.{RESET}")
                break
    except KeyboardInterrupt:
        try:
            sock.sendall("/salir".encode("utf-8"))
        except OSError:
            pass

    try:
        sock.close()
    except OSError:
        pass
    print(f"{FG_YELLOW}Cerrando cliente...{RESET}")


if __name__ == "__main__":
    main()


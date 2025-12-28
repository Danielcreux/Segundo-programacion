#!/usr/bin/env python3
import socket
import threading

HOST = "0.0.0.0"   # Escuchar en todas las interfaces
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

clientes = {}  # socket -> apodo
lock_clientes = threading.Lock()


def imprimir_banner():
    banner = f"""
{FG_CYAN}{BOLD}╔═══════════════════════════════════════════════╗
║              💬  SERVIDOR DE CHAT PYTHON        ║
║        Multiusuario · UTF-8 · Emojis 🙂        ║
╚═══════════════════════════════════════════════╝{RESET}
"""
    print(banner)


def enviar_a_todos(mensaje: str, sock_remitente: socket.socket | None = None) -> None:
    """Envía un mensaje a todos los clientes excepto al remitente."""
    datos = mensaje.encode("utf-8", errors="ignore")
    with lock_clientes:
        desconectados = []
        for s in clientes:
            if s is sock_remitente:
                continue
            try:
                s.sendall(datos)
            except OSError:
                desconectados.append(s)

        # Eliminar clientes desconectados
        for s in desconectados:
            apodo = clientes.get(s, "Desconocido")
            del clientes[s]
            print(f"{FG_RED}[DESCONECTADO]{RESET} {apodo} (error de socket)")


def manejar_cliente(conn: socket.socket, addr) -> None:
    try:
        conn.sendall("🟢 Bienvenido. Escribe tu apodo: ".encode("utf-8"))
        apodo_bytes = conn.recv(64)
        if not apodo_bytes:
            conn.close()
            return

        apodo = apodo_bytes.decode("utf-8", errors="ignore").strip()
        if not apodo:
            apodo = f"{addr[0]}:{addr[1]}"

        with lock_clientes:
            clientes[conn] = apodo

        mensaje_union = f"👤 {apodo} se ha unido al chat.\n"
        print(f"{FG_GREEN}[UNIÓN]{RESET} {apodo} desde {addr}")
        enviar_a_todos(mensaje_union)

        conn.sendall("✅ Ya estás conectado. Escribe /salir para desconectarte.\n".encode("utf-8"))

        # Bucle de mensajes
        while True:
            datos = conn.recv(1024)
            if not datos:
                break

            texto = datos.decode("utf-8", errors="ignore").strip()
            if texto == "":
                continue

            if texto.lower() == "/salir":
                break

            mensaje = f"💬 {apodo}: {texto}\n"
            print(f"{FG_MAGENTA}[MENSAJE]{RESET} {apodo}: {texto}")
            enviar_a_todos(mensaje, sock_remitente=conn)

    except ConnectionResetError:
        pass
    finally:
        with lock_clientes:
            apodo = clientes.pop(conn, "Desconocido")
        conn.close()

        mensaje_salida = f"🚪 {apodo} ha salido del chat.\n"
        print(f"{FG_YELLOW}[SALIDA]{RESET} {apodo}")
        enviar_a_todos(mensaje_salida)


def main():
    imprimir_banner()
    print(f"{DIM}Escuchando en {HOST}:{PORT} ...{RESET}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((HOST, PORT))
        servidor.listen()

        while True:
            try:
                conn, addr = servidor.accept()
            except KeyboardInterrupt:
                print(f"\n{FG_RED}Cerrando servidor...{RESET}")
                break

            hilo = threading.Thread(target=manejar_cliente, args=(conn, addr), daemon=True)
            hilo.start()


if __name__ == "__main__":
    main()


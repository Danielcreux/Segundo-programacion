# servidor.py (compatible con websockets >= 11)
import asyncio
import itertools
import websockets
from websockets.exceptions import ConnectionClosed

CONNECTED = {}                 # {client_id: websocket}
ID_SEQ = itertools.count(1)

def print_connected(prefix=""):
    if not CONNECTED:
        print(f"{prefix}No hay clientes conectados.")
        return
    print(f"{prefix}Clientes conectados ({len(CONNECTED)}):")
    for cid, ws in CONNECTED.items():
        peer = getattr(ws, "remote_address", None)
        print(f"  - #{cid} {peer}")

async def keepalive(ws, cid, interval=30, timeout=10):
    while True:
        await asyncio.sleep(interval)
        try:
            pong_waiter = await ws.ping()
            await asyncio.wait_for(pong_waiter, timeout=timeout)
        except Exception as e:
            print(f"[#{cid}] ping falló ({e}). Cerrando conexión…")
            try:
                await ws.close(code=1002, reason="Ping timeout")
            finally:
                break

async def register(ws):
    cid = next(ID_SEQ)
    CONNECTED[cid] = ws
    peer = getattr(ws, "remote_address", None)
    path = getattr(ws, "path", None)  # websockets >=11
    print(f"Conectado #{cid} desde {peer} path={path}")
    print_connected(prefix="> ")
    return cid

async def unregister(cid):
    CONNECTED.pop(cid, None)
    print(f"Desconectado #{cid}")
    print_connected(prefix="> ")

# *** IMPORTANT: single-arg handler for websockets >= 11 ***
async def handler(ws):
    cid = await register(ws)
    ka_task = asyncio.create_task(keepalive(ws, cid))
    try:
        async for msg in ws:
            await ws.send(f"echo: {msg}")
    except ConnectionClosed as e:
        print(f"[#{cid}] conexión cerrada: {e.code} {e.reason}")
    finally:
        ka_task.cancel()
        await unregister(cid)

async def main():
    # ping_interval=None para usar nuestro keepalive explícito
    async with websockets.serve(
        handler,
        host="127.0.0.1",
        port=8765,
        ping_interval=None,
        max_queue=32,
    ):
        print("Servidor WebSocket en ws://127.0.0.1:8765 listo.")
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSaliendo…")

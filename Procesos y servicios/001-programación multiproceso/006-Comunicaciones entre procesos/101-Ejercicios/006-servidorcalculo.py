# servidor.py
import asyncio
import itertools
import json
import websockets
from websockets.exceptions import ConnectionClosed

TASK_SEQ = itertools.count(1)
CLIENTS = {}  # {cid: ws}
ID_SEQ = itertools.count(1)

async def send_task(ws, *, initial: float, factor: float, times: int):
    task_id = next(TASK_SEQ)
    payload = {
        "type": "task",
        "op": "repeat_multiply",
        "task_id": task_id,
        "initial": initial,
        "factor": factor,
        "times": times,
    }
    await ws.send(json.dumps(payload))
    return task_id

def list_clients():
    if not CLIENTS:
        print("No hay clientes conectados.")
        return
    print(f"Clientes conectados ({len(CLIENTS)}):")
    for cid, ws in CLIENTS.items():
        print(f"  - #{cid} {getattr(ws,'remote_address',None)}")

async def handler(ws):
    cid = next(ID_SEQ)
    CLIENTS[cid] = ws
    print(f"Conectado #{cid} desde {getattr(ws,'remote_address',None)} path={getattr(ws,'path',None)}")
    list_clients()

    # Send the computation task immediately on connect:
    task_id = await send_task(
        ws,
        initial=1.0000054,
        factor=1.00000043,
        times=1_000_000
    )
    print(f"[#{cid}] Tarea enviada task_id={task_id}")

    try:
        async for raw in ws:
            try:
                msg = json.loads(raw)
            except Exception:
                print(f"[#{cid}] Mensaje no-JSON: {raw!r}")
                continue

            if msg.get("type") == "result" and msg.get("task_id") == task_id:
                result = msg.get("result")
                duration = msg.get("duration_ms")
                ua = msg.get("agent")
                print(f"[#{cid}] ✅ Resultado task_id={task_id}")
                print(f"          result={result}")
                if duration is not None:
                    print(f"          duration_ms={duration}")
                if ua:
                    print(f"          agent={ua}")
            else:
                # Echo other messages or handle more ops
                pass

    except ConnectionClosed as e:
        print(f"[#{cid}] conexión cerrada: {e.code} {e.reason}")
    finally:
        CLIENTS.pop(cid, None)
        print(f"Desconectado #{cid}")
        list_clients()

async def main():
    async with websockets.serve(
        handler,
        host="127.0.0.1",
        port=8765,
        ping_interval=None,   # we'll keep it simple; rely on TCP (add your own keepalive if you want)
    ):
        print("Servidor WebSocket en ws://127.0.0.1:8765 listo.")
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSaliendo…")

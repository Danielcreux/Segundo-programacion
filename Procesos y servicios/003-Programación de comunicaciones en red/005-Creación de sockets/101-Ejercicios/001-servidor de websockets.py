#!/usr/bin/env python3
import asyncio
import json
import ssl
import websockets

connected_clients = set()

async def handler(websocket, path):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            # Expect JSON
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    "type": "error",
                    "error": "invalid_json"
                }))
                continue

            # Broadcast received JSON to all clients
            payload = json.dumps(data)

            disconnected = []
            for client in connected_clients:
                if client.closed:
                    disconnected.append(client)
                    continue
                try:
                    await client.send(payload)
                except Exception:
                    disconnected.append(client)

            # Clean up
            for client in disconnected:
                connected_clients.discard(client)

    finally:
        connected_clients.discard(websocket)

async def main():
    # TLS context using your existing cert and key
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(
        certfile="/etc/apache2/ssl/jocarsa_combined.cer",
        keyfile="/etc/apache2/ssl/jocarsa.key"
    )

    # Listen on port 8766 with TLS
    async with websockets.serve(
        handler,
        "0.0.0.0",
        8766,
        ssl=ssl_context
    ):
        print("Secure WebSocket server on wss://jocarsa.com:8766")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())


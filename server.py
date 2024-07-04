import asyncio
import websockets
from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
import threading
import signal
import sys
import webbrowser

clients = set()

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        elif self.path == '/resultado':
            self.path = '/resultado.html'
        return super().do_GET()

def start_http_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, MyHandler)
    print("Servidor HTTP rodando na porta 8000")
    httpd.serve_forever()

def start_websocket_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_server = websockets.serve(handler, '0.0.0.0', 3000)
    loop.run_until_complete(start_server)
    print("Servidor WebSocket rodando na porta 3000")
    loop.run_forever()

async def handler(websocket, path):
    global clients
    clients.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            for client in clients:
                if client != websocket:
                    await client.send(message)
    finally:
        clients.remove(websocket)

def signal_handler(sig, frame):
    print("\nEncerrando servidores...")
    sys.exit(0)

def open_browser():
    try:
        webbrowser.open("http://localhost:8000")
    except Exception as e:
        print(f"Erro ao abrir o navegador: {e}")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    # Iniciar servidor HTTP em uma thread separada
    http_thread = threading.Thread(target=start_http_server)
    http_thread.start()

    # Abrir o navegador após um curto intervalo para garantir que o servidor HTTP esteja ativo
    threading.Timer(2.0, open_browser).start()

    # Iniciar servidor WebSocket no thread principal
    start_websocket_server()

    # Aguardar o término do servidor HTTP antes de encerrar
    http_thread.join()

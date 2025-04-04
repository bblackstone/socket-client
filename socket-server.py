import socket
import subprocess
import sys
import threading
import argparse

# Try to import pyngrok for external tunneling
try:
    from pyngrok import ngrok
    NGROK_ENABLED = True
except ImportError:
    NGROK_ENABLED = False

# For WebSocket server support
try:
    import asyncio
    import websockets
    WS_ENABLED = True
except ImportError:
    WS_ENABLED = False

# Server configuration
HOST = "0.0.0.0"
PORT = 17100
PASSWORD = "bs-atlas"  # Change this as needed

# Ngrok setup (using HTTP tunnels for free accounts)
public_url = None
if NGROK_ENABLED:
    try:
        ngrok.set_auth_token("2vEyYAqpe58ExZkDvSordRvWnXe_52EpfaExEAgcxmT8pP2Pp")
        public_url = ngrok.connect(PORT, "http")
        print(f"Ngrok Tunnel Established: {public_url}")
    except Exception as e:
        print("Error establishing ngrok tunnel:", e)
        print("  Ensure you have a verified ngrok account and have set your authtoken.")
        public_url = None
else:
    print("pyngrok not installed; external tunneling not available.")

#
# Raw TCP Socket Server Implementation
#
def handle_tcp_client(conn, addr):
    """Handles client authentication and command execution over a TCP connection."""
    print(f"Connected by {addr}")

    if public_url:
        conn.sendall(f"Server Public Address: {public_url}\n".encode())

    conn.sendall(b"Enter password: ")
    auth = conn.recv(1024).decode().strip()

    if auth != PASSWORD:
        conn.sendall(b"Authentication failed.\n")
        conn.close()
        return

    conn.sendall(b"Authentication successful. You can now send commands.\n")

    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break

            message = data.decode().strip()
            if message.startswith("cmd "):
                command = message[4:].strip()
                try:
                    result = subprocess.check_output(
                        command, shell=True, stderr=subprocess.STDOUT, text=True
                    )
                except subprocess.CalledProcessError as e:
                    result = e.output or "Command execution failed."
                conn.sendall(result.encode() if result else b"Command executed.\n")
            else:
                print(f"Message received: {message}")
                response = input("Enter response: ")
                conn.sendall(response.encode())
        except Exception as e:
            print(f"Connection error with {addr}: {e}")
            break

    print(f"Connection closed: {addr}")
    conn.close()

def start_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server listening on port {PORT} (TCP)...")
    while True:
        try:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle_tcp_client, args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("\nServer shutting down...")
            server_socket.close()
            sys.exit()

#
# WebSocket Server Implementation
#
async def handle_ws_client(websocket, path):
    """Handles client authentication and command execution over WebSocket."""
    if public_url:
        await websocket.send(f"Server Public Address: {public_url}\n")

    await websocket.send("Enter password:")
    auth = await websocket.recv()

    if auth.strip() != PASSWORD:
        await websocket.send("Authentication failed.")
        await websocket.close()
        return

    await websocket.send("Authentication successful. You can now send commands.")

    while True:
        try:
            message = await websocket.recv()
            if message.startswith("cmd "):
                command = message[4:].strip()
                try:
                    result = subprocess.check_output(
                        command, shell=True, stderr=subprocess.STDOUT, text=True
                    )
                except subprocess.CalledProcessError as e:
                    result = e.output or "Command execution failed."
                await websocket.send(result if result else "Command executed.")
            else:
                # Echo regular messages back
                await websocket.send(f"Echo: {message}")
        except Exception as e:
            print(f"WebSocket connection error: {e}")
            break
    print("WebSocket connection closed.")

async def start_ws_server():
    server = await websockets.serve(handle_ws_client, HOST, PORT)
    print(f"WebSocket server listening on port {PORT}...")
    await server.wait_closed()

#
# Main entry point: choose between TCP and WebSocket server
#
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Dual-mode Server: TCP socket or WebSocket")
    parser.add_argument("--mode", choices=["tcp", "ws"], default="tcp", help="Select server mode (tcp or ws)")
    args = parser.parse_args()

    if args.mode == "tcp":
        start_tcp_server()
    else:
        if not WS_ENABLED:
            print("Websockets library not installed. Install with: pip install websockets")
            sys.exit(1)
        try:
            asyncio.run(start_ws_server())
        except KeyboardInterrupt:
            print("\nWebSocket server shutting down...")
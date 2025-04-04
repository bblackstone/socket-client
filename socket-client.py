import sys
import argparse
import socket

# Try to import websocket client library for WebSocket mode
try:
    import websocket
    WS_CLIENT_AVAILABLE = True
except ImportError:
    WS_CLIENT_AVAILABLE = False

HOST = "127.0.0.1"  # Default; override with --host if needed
PORT = 17100
PASSWORD = "bs-atlas"  # Same as server password

def tcp_client():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    print("Connected to TCP server.")

    # Display initial messages (for example, public URL and password prompt)
    data = s.recv(1024).decode()
    print(data, end="")

    # Send password
    s.sendall(PASSWORD.encode())
    resp = s.recv(1024).decode()
    print(resp, end="")

    # Interactive loop: send user input to server and print the response
    try:
        while True:
            user_input = input(">> ")
            s.sendall(user_input.encode())
            response = s.recv(4096).decode()
            print(response)
    except KeyboardInterrupt:
        print("\nClosing connection.")
    finally:
        s.close()

def ws_client():
    if not WS_CLIENT_AVAILABLE:
        print("Websocket client library not installed. Install with: pip install websocket-client")
        sys.exit(1)

    ws_url = f"ws://{HOST}:{PORT}"
    ws = websocket.create_connection(ws_url)
    print("Connected to WebSocket server.")

    # Display initial messages from the server
    result = ws.recv()
    print(result, end="")

    # Send password and display confirmation
    ws.send(PASSWORD)
    result = ws.recv()
    print(result, end="")

    # Interactive loop: send messages and display response
    try:
        while True:
            user_input = input(">> ")
            ws.send(user_input)
            result = ws.recv()
            print(result)
    except KeyboardInterrupt:
        print("\nClosing connection.")
    finally:
        ws.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Dual-mode Client: TCP socket or WebSocket")
    parser.add_argument("--mode", choices=["tcp", "ws"], default="tcp", help="Select client mode (tcp or ws)")
    parser.add_argument("--host", default=HOST, help="Server host address")
    parser.add_argument("--port", type=int, default=PORT, help="Server port")
    args = parser.parse_args()

    # Override host and port if provided
    HOST = args.host
    PORT = args.port

    if args.mode == "tcp":
        tcp_client()
    else:
        ws_client()
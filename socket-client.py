import sys
import argparse

# Try to import websocket client library for WebSocket mode
try:
    import websocket
    WS_CLIENT_AVAILABLE = True
except ImportError:
    WS_CLIENT_AVAILABLE = False

HOST = "127.0.0.1"  # Default; can be overridden by --host
PORT = 17100        # Default; can be overridden by --port
PASSWORD = "bs-atlas"  # Same as server password

def tcp_client():
    print("TCP mode is not compatible with Ngrok HTTP tunnels. Use WebSocket mode instead.")
    sys.exit(1)

def ws_client(ws_url):
    if not WS_CLIENT_AVAILABLE:
        print("websocket-client library not installed. Install with: pip install websocket-client")
        sys.exit(1)

    ws = websocket.create_connection(ws_url)
    print(f"Connected to WebSocket server at {ws_url}")

    # Display initial messages from the server
    msg = ws.recv()
    print(msg, end="")

    # Send password and display confirmation
    ws.send(PASSWORD)
    msg = ws.recv()
    print(msg, end="")

    # Interactive loop: send messages and display response
    try:
        while True:
            user_input = input(">> ")
            ws.send(user_input)
            msg = ws.recv()
            print(msg)
    except KeyboardInterrupt:
        print("\nClosing connection.")
    finally:
        ws.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Dual-mode Client: TCP or WebSocket")
    parser.add_argument("--mode", choices=["tcp", "ws"], default="ws", help="Select client mode (tcp or ws)")
    parser.add_argument("--url", help="Full WebSocket URL (e.g., wss://7dbf-197-230-172-163.ngrok-free.app)")
    parser.add_argument("--host", help="Server host address (if not using a full URL)")
    parser.add_argument("--port", type=int, help="Server port (if not using a full URL)")
    args = parser.parse_args()

    if args.mode == "tcp":
        tcp_client()
    else:
        # For WebSocket mode, use --url if provided, otherwise use host/port
        if args.url:
            ws_url = args.url
        else:
            if not args.host or not args.port:
                print("Provide either --url or both --host and --port for WebSocket mode.")
                sys.exit(1)
            protocol = "wss" if args.host.startswith("https") or "ngrok" in args.host else "ws"
            ws_url = f"{protocol}://{args.host}:{args.port}"
        ws_client(ws_url)
import socket
import subprocess
import sys
import threading

# Try to import pyngrok for external tunneling
try:
    from pyngrok import ngrok
    NGROK_ENABLED = True
except ImportError:
    NGROK_ENABLED = False

# Server configuration
HOST = "0.0.0.0"
PORT = 17100
PASSWORD = "bs-atlas"  # Change this to your desired password

# Start Ngrok if available and authenticated
public_url = None
if NGROK_ENABLED:
    try:
        # Uncomment and set your authtoken if you have a verified account:
        # ngrok.set_auth_token("YOUR_AUTHTOKEN")
        tunnel = ngrok.connect(PORT, "tcp")
        public_url = tunnel.public_url.replace("tcp://", "")
        print(f" Ngrok Tunnel Established: {public_url}")
    except Exception as e:
        print("Error establishing ngrok tunnel:", e)
        print("  Ensure you have a verified ngrok account and have set your authtoken.")
        public_url = None
else:
    print("  pyngrok not installed; external tunneling not available.")

# Start the server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(f" Server listening on port {PORT}...")

def handle_client(conn, addr):
    """Handles client authentication and command execution."""
    print(f"🔗 Connected by {addr}")

    # Send Ngrok public URL if available
    if public_url:
        conn.sendall(f"Server Public Address: {public_url}\n".encode())

    # Authentication
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
            print(f"  Connection error: {e}")
            break

    print(f"🔌 Connection closed: {addr}")
    conn.close()

# Accept multiple clients
while True:
    try:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\n Server shutting down...")
        server_socket.close()
        sys.exit()
import socket


# Server setup

HOST = "0.0.0.0"
PORT = 17100  # Ensure this is within 0-65535

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

print(f"Server listening on port {PORT}...")

conn, addr = server_socket.accept()
print(f"Connected by {addr}")

while True:
    data = conn.recv(1024)
    if not data:
        break
    print(f"Received: {data.decode()}")
    response = input("Enter response: ")
    conn.sendall(response.encode())

conn.close()
server_socket.close()
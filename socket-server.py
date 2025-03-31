import socket


# Server setup

HOST = "0.0.0.0"
PORT = 171007

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Server listening on {HOST}:{PORT}...")

conn, addr = server_socket.accept()

print(f"Connected by {addr}")

while True:
    data = conn.recv(1024).decode()
    if not data:
        break
    print(f"Received: {data}")



    conn.sendall(f"Echo: {data}".encode())

conn.close
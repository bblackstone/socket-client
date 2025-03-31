import socket

# Connect to server

SERVER_IP = "192.168.1.5"
PORT = 17100  # Ensure this is within 0-65535

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, PORT))
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
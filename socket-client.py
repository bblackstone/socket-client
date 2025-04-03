import socket

# Connect to server
SERVER_IP = input("Enter the Server IPV4 or hostname: ")
PORT = 17100

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, PORT))
print(f"Connected to server at {SERVER_IP}:{PORT}")

# Wait for an initial message from the server (e.g. authentication prompt)
initial_msg = client_socket.recv(1024).decode()
print(f"Server: {initial_msg}")

while True:
    msg = input("Enter message: ")
    if msg.lower() == "exit":
        break
    client_socket.sendall(msg.encode())
    response = client_socket.recv(1024).decode()
    print(f"Server: {response}")

client_socket.close()
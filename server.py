import socket

HOST = '' 
PORT = 50000 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
print("Waiting for response from client at port ",PORT)
conn, addr = s.accept()
print('Connected by', addr)
conn.sendall("Welcome to the server".encode())

while True:
    data = conn.recv(1024)
    print(data)
    if not data: break
    conn.sendall(data)    
conn.close()
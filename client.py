import socket
import sys
import time
 
# Create a connection to the server application on port 81
tcp_socket = socket.create_connection(('169.254.15.3', 4000))
tcp_socket.setblocking(0)


timer = time.time()
count = 0
msg1 = 'warming up...'
msg2 = '...'
msg3 = 'ready'

data = 'Hi. I am a TCP client sending data to the server'
tcp_socket.sendall(data.encode())

while True:
	if time.time() - timer > 2:
		break

try:
	data = tcp_socket.recv(1024)
	print(data)
except:
	print("data")

print("Closing socket")
tcp_socket.close()

import socket
import sys
import time
 
# Create a connection to the server application on port 81
#tcp_socket = socket.create_connection(('192.168.137.1', 4000))
tcp_socket = socket.create_connection(('localhost', 4000))


timer = time.time()
count = 0
msg1 = 'warming up...'
msg2 = '...'
msg3 = 'ready'

while True:
    # True every 5 seconds
    if time.time() - timer > 2.5:
        tcp_socket.sendall(msg1.encode())
        count += 1
        timer = time.time()
        if count == 5:
            tcp_socket.sendall(msg3.encode())
            break

#try:
#    data = 'Hi. I am a TCP client sending data to the server'
#    tcp_socket.sendall(data.encode())

#finally:
print("Closing socket")
tcp_socket.close()

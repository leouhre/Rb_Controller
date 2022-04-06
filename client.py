import socket
import sys
 
# Create a connection to the server application on port 81
tcp_socket = socket.create_connection(('192.168.137.1', 4000))
 
try:
    data = 'Hi. I am a TCP client sending data to the server'
    tcp_socket.sendall(data.encode())
 
finally:
    print("Closing socket")
    tcp_socket.close()

import socket

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)   
# AF_NET :  address family  
# SOCK_Stream : we are using TCP. WHY?  to ensure reliable and secure connection and ordered sequence of packets.

server.bind(("127.0.0.1",5000))
#IP:  127.0.0.1 (local host ip) and server program is going to be listened to at port 5000
#if i use 0.0.0.0 then any device on my Local network can connect to it

server.listen() #listening socket which wilk accept all connections from clients

print("Welcoming socket established and listening at port:5000")

while True:

    client_socket, address = server.accept() # blocking call. The server creates a new server side client socket for each connection approved and waits if not

    data = client_socket.recv(1024)

    message = data.decode()

    print("Message from",address," client :", message)

    client_socket.send("Hello client".encode())

    client_socket.close()



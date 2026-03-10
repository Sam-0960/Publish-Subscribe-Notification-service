import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#here we do not bind the socket into a particular port.
#Reasons: 1. Port is given by the OS itself
#         2. IP is obtained and assigned by os via DHCP protocol


client.connect(("127.0.0.1", 5000)) #connect the ip to the local server
#incase of a server located at some other part of the world then the s

client.send("boss".encode())

data = client.recv(1024)

print("Server replied:", data.decode())

client.close()
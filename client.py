import socket
import ssl
import threading


def receive_messages(sock):

    while True:

        try:
            data = sock.recv(1024)

            if not data:
                break

            print("\n" + data.decode())

        except:
            break


context = ssl._create_unverified_context()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client = context.wrap_socket(client)

client.connect(("127.0.0.1", 5000))

print("Connected to secure server")

thread = threading.Thread(target=receive_messages, args=(client,))
thread.start()

while True:

    message = input("-> ")

    client.send(message.encode())
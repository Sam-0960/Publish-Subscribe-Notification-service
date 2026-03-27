import socket
import ssl
import threading
import time

SERVER_IP = "127.0.0.1"   # your IP
PORT = 5000

NUM_CLIENTS = 10              # change this
SEND_DELAY = 0.01             # lower = more load


def client_task(cid):
    context = ssl._create_unverified_context()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client = context.wrap_socket(client)

    client.connect((SERVER_IP, PORT))

    client.send("SUBSCRIBE sports".encode())

    while True:
        try:
            client.send(f"PUBLISH sports msg_{cid}".encode())
            time.sleep(SEND_DELAY)
        except:
            break


threads = []

for i in range(NUM_CLIENTS):
    t = threading.Thread(target=client_task, args=(i,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()
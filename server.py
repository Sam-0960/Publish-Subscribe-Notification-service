import socket
import threading
import ssl

topics = {}
topics_lock = threading.Lock()

# to remove dead sockets
def remove_client_from_topics(client_socket):
    with topics_lock:
        for topic in topics:
            if client_socket in topics[topic]:
                topics[topic].remove(client_socket)   



def handle_client(client_socket, address):
    print("Client connected:", address)
    #persistent connection loop
    while True:
        data = client_socket.recv(1024)

        if not data:
            break

        message = data.decode().strip()
        parts = message.split()
        command = parts[0]

        if not parts:
            continue

        if command == "SUBSCRIBE":
            topic = parts[1]
            with topics_lock:
                if topic not in topics:
                    topics[topic] = []

                topics[topic].append(client_socket)
            print(address, "subscribed to", topic)

        elif command == "PUBLISH":

            topic = parts[1]
            msg = " ".join(parts[2:])

            with topics_lock:
                subscribers = list(topics.get(topic, []))

            for sub in subscribers:
                sub.send(f"{topic}: {msg}".encode())

        elif command == "UNSUBSCRIBE":

            topic = parts[1]

            with topics_lock:

                if topic in topics and client_socket in topics[topic]:
                    topics[topic].remove(client_socket)

            print(address, "unsubscribed from", topic)
        

        print("Message from", address, ":", message)
        client_socket.send("ACK".encode())
    
    remove_client_from_topics(client_socket)   

    client_socket.close()
    print("Client disconnected:", address)


#establishing the permanent server listening socket
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="server.crt", keyfile="server.key")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 5000))
server.listen(5)

server = context.wrap_socket(server, server_side=True)

print("Server running on port 5000")

while True:
    client_socket, client_address = server.accept()
    #create a thread for each client and run them simultaneously using multi-threading
    thread = threading.Thread(
        target=handle_client,
        args=(client_socket, client_address),
        daemon=True
    )

    thread.start()
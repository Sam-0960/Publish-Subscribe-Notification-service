import socket
import threading
import ssl
import time


# SHARED memory between multiple clients
topics = {}
topics_lock = threading.Lock()

# METRICS
messages_sent = 0
messages_received = 0
start_time = time.time()
metrics_lock = threading.Lock()


# to remove dead sockets
def remove_client_from_topics(client_socket):
    with topics_lock:
        for topic in topics:
            if client_socket in topics[topic]:
                topics[topic].remove(client_socket)


def handle_client(client_socket, address):
    global messages_sent, messages_received

    print("Client connected:", address)

    while True:
        try:
            data = client_socket.recv(1024)

            if not data:
                break

            message = data.decode().strip()

            # track received messages
            with metrics_lock:
                messages_received += 1

            parts = message.split()

            if not parts:
                continue

            command = parts[0]

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
                    try:
                        sub.send(f"{topic}: {msg}".encode())

                        # track sent messages
                        with metrics_lock:
                            messages_sent += 1

                    except:
                        pass

            elif command == "UNSUBSCRIBE":

                topic = parts[1]

                with topics_lock:
                    if topic in topics and client_socket in topics[topic]:
                        topics[topic].remove(client_socket)

                print(address, "unsubscribed from", topic)

            print("Message from", address, ":", message)

            client_socket.send("ACK".encode())

        except:
            break

    remove_client_from_topics(client_socket)
    client_socket.close()
    print("Client disconnected:", address)


#  METRICS PRINTER THREAD
def print_metrics():
    global messages_sent, messages_received

    while True:
        time.sleep(5)

        elapsed = time.time() - start_time

        with metrics_lock:
            sent = messages_sent
            received = messages_received

        print("\n===== PERFORMANCE =====")
        print("Time:", round(elapsed, 2), "sec")
        print("Messages Received:", received)
        print("Messages Sent:", sent)
        print("Throughput:", round(sent / elapsed, 2), "msg/sec")
        print("=======================\n")


# SSL setup
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="server.crt", keyfile="server.key")


# Server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 5000))
server.listen(5)

server = context.wrap_socket(server, server_side=True)

print("Server running on port 5000")


#  start metrics thread
threading.Thread(target=print_metrics, daemon=True).start()


while True:
    client_socket, client_address = server.accept()

    thread = threading.Thread(
        target=handle_client,
        args=(client_socket, client_address),
        daemon=True
    )

    thread.start()

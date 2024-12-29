# server.py
import socket
import threading
import ssl
from config import HOST, PORT, PASSWORD

# Create socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

# SSL context
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile="server.crt", keyfile="server.key")
server = context.wrap_socket(server, server_side=True)

# Store client connections
clients = []

def broadcast(message):
    """Send message to all connected clients"""
    for client in clients:
        client.send(message)

def handle_client(client):
    """Handle individual client connection"""
    try:
        # First verify password
        auth = client.recv(1024).decode('utf-8')
        if auth != PASSWORD:
            client.send("Invalid password".encode('utf-8'))
            client.close()
            return
        
        client.send("Connected to server!".encode('utf-8'))
        
        while True:
            try:
                message = client.recv(1024)
                broadcast(message)
            except:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                break
    except:
        client.close()

def main():
    print("Server is running...")
    while len(clients) < 2:  # Accept only 2 clients
        try:
            client, address = server.accept()
            print(f"Connected with {str(address)}")
            
            clients.append(client)
            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start()
            
            if len(clients) == 2:
                broadcast("Chat can begin now!".encode('utf-8'))
        except Exception as e:
            print(f"Error: {e}")
            continue

if __name__ == "__main__":
    main()

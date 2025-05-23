import socket
import threading
import json

HOST = 'localhost'
PORT = 12345

clients = {}
character_sheets = {}

def handle_client(conn, addr):
    print(f"[+] New connection from {addr}")
    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break

            message = json.loads(data)
            username = message.get("username")

            if message["type"] == "register":
                character_sheets[username] = message["character"]
                clients[username] = conn
                print(f"[+] Registered: {username}")
            elif message["type"] == "roll":
                print(f"[{username}] rolled {message['dice']}: {message['result']}")
            elif message["type"] == "get_all_characters":
                response = {"type": "all_characters", "data": character_sheets}
                conn.send(json.dumps(response).encode())
    except Exception as e:
        print(f"[!] Error with client {addr}: {e}")
    finally:
        if username in clients:
            del clients[username]
        if username in character_sheets:
            del character_sheets[username]
        conn.close()
        print(f"[-] Disconnected {addr}")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[+] Server started on {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start_server()

#server.py

import socket
import threading

def client_thread(conn, addr, clients, nicknames, secret_key):
    try:
        key = conn.recv(1024).decode()
        if key != secret_key:
            conn.send("Falha na conexão: chave incorreta.".encode())
            conn.close()
            return
        
        welcome_message = "Você está conectado ao servidor."
        conn.send(welcome_message.encode())

        nickname = conn.recv(1024).decode()
        nicknames[conn] = nickname
        broadcast(f"{nickname} entrou no chat.", conn, clients)

        while True:
            message = conn.recv(1024).decode()
            if not message:
                break
            if message == '###listar':
                listar_usuarios(conn, nicknames)
            elif message.startswith('###'):
                _, recipient, msg = message.split(':', 2)
                send_private(f"{nicknames[conn]}: {msg.strip()}", recipient.strip(), conn, clients, nicknames)
            else:
                broadcast(message, conn, clients)
    finally:
        if conn in nicknames:
            broadcast(f"{nicknames[conn]} saiu do chat.", conn, clients)
            nickname = nicknames[conn]
            conn.close()
            clients.remove(conn)
            del nicknames[conn]
            print(f"{nickname} desconectado.")

def listar_usuarios(sender, nicknames):
    usuarios = ', '.join(nick for nick in nicknames.values())
    sender.send(f"Usuários conectados: {usuarios}".encode())

def broadcast(message, sender, clients):
    # Verificar se a mensagem é um comando antes de transmitir
    if not message.startswith('###'):
        for client in clients:
            if client != sender:
                client.send(message.encode())

def send_private(message, recipient, sender, clients, nicknames):
    found = False
    for client, nick in nicknames.items():
        if nick == recipient:
            client.send(f"###{nick}: {message}".encode())
            found = True
            break
    if not found:
        sender.send(f"Usuário {recipient} não encontrado.".encode())

def list_users(sender, nicknames):
    users_list = "Usuários online: " + ", ".join(nicknames.values())
    sender.send(users_list.encode())

def main():
    secret_key = "chave123"
    host = 'localhost'
    port = 12345
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()

    print("Servidor rodando. Aguardando conexões...")
    
    clients = []
    nicknames = {}

    while True:
        conn, addr = server_socket.accept()
        print(f"Conexão de {addr}")
        clients.append(conn)
        thread = threading.Thread(target=client_thread, args=(conn, addr, clients, nicknames, secret_key))
        thread.start()

if __name__ == "__main__":
    main()

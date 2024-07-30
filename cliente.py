# cliente.py

import socket
import threading

def receive_messages(sock):
    while True:
        try:
            message = sock.recv(1024).decode()
            if message:
                print(message)
            else:
                break
        except:
            print("Você foi desconectado do servidor.")
            sock.close()
            break

def main():
    host = 'localhost'
    port = 12345
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    # Envia a chave secreta para o servidor
    secret_key = "chave123"
    client_socket.send(secret_key.encode())

    response = client_socket.recv(1024).decode()
    if "Falha na conexão" in response:
        print(response)
        return

    nickname = input("Digite seu identificador (nickname): ")
    client_socket.send(nickname.encode())
    print("-------------------------")
    print("Conectado ao servidor.")
    print("Digite 'sair' para sair.")
    print("Use '@nome Mensagem' para enviar uma mensagem privada.")
    print("Digite 'listar' para listar os usuários.")
    print("-------------------------")

    thread = threading.Thread(target=receive_messages, args=(client_socket,))
    thread.start()

    while True:
        message = input()
        if message == "sair":
            break
        elif message == "listar":
            client_socket.send("###listar".encode())
            print("Listando usuários...")
        elif message.startswith('@'):
            recipient, *msg = message.split(' ', 1)
            message = f"###:{recipient[1:]}:{' '.join(msg)}"
            client_socket.send(message.encode())
            print(f"Mensagem privada para {recipient[1:]}: {' '.join(msg)}")
        else:
            message = f"{nickname}: {message}"
            print(f"Você: {message}")
            client_socket.send(message.encode())


    client_socket.close()

if __name__ == "__main__":
    main()

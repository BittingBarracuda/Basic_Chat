import socket
import threading

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8080

def listen_to_server(client_socket):
    while True:
        text = client_socket.recv(1024).decode()
        print(text)

def init_chat():
    user_name = input('[+] Type in your username: ')
    client_socket = socket.socket()
    try:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        client_socket.send(user_name.encode('utf-8'))
        thread = threading.Thread(target=listen_to_server, args=(client_socket,))
        thread.start()
        while True:
            text = input(f'{user_name}> ')
            client_socket.send(f'{user_name}> {text}'.encode('utf-8'))
    except Exception as e:
        print(f'[*] Error connecting to server: {e}')

if __name__ == "__main__":
    init_chat()
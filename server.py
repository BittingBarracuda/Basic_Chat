import socket
import threading
import getpass
import sys
import random

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8080
lock = threading.Lock()
waiting_condition = threading.Condition()
clients = []  

class Client():
    def __init__(self, conn, addr, user_name):
        self.conn = conn
        self.addr = addr
        self.user_name = user_name

    def __repr__(self):
        return f'{self.user_name} -> ({self.addr[0]}, {str(self.addr[1])})'

class ChatThread(threading.Thread):
    def __init__(self, source, destiny):
        super().__init__()
        self.source = source
        self.destiny = destiny

    @staticmethod
    def __check_connection(connection):
        try:
            connection.send(b'<PING>')
            return True
        except:
            return False

    def run(self):
        self.destiny.conn.send(f'[+] Connected with {self.source.user_name}!'.encode('utf-8'))
        while True:
            try:
                text = self.source.conn.recv(1024)
                self.destiny.conn.send(text)
            except Exception as e:
                print(f'[!] Error: {e}')
                if not ChatThread.__check_connection(self.source.conn):
                    if ChatThread.__check_connection(self.destiny.conn):
                        self.destiny.conn.send(f'[!] User {self.source.user_name} disconnected!\n[+] Waiting for another user to connect...'.encode('utf-8'))
                        lock.acquire()
                        clients.append(self.destiny)
                        lock.release()
                else:
                    self.source.conn.send(f'[!] User {self.destiny.user_name} disconnected!\n[+] Waiting for another user to connect...'.encode('utf-8'))
                    lock.acquire()
                    clients.append(self.source)
                    lock.release()
                break

def connection_handler():
    while True:
        with waiting_condition:
            lock.acquire()
            if len(clients) <= 1:
                lock.release()
                waiting_condition.wait()
            else:
                last_client = clients.pop()
                random_client = random.choice(clients)
                clients.remove(random_client)
                lock.release()
                print(f'[+] Chat established between {last_client} && {random_client}')
                thread1 = ChatThread(last_client, random_client)
                thread2 = ChatThread(random_client, last_client)
                thread1.daemon = True
                thread2.daemon = True
                thread1.start()
                thread2.start()
    
def login_user(conn, addr):
    try:
        resp = conn.recv(1024).decode()
        lock.acquire()
        client = Client(conn, addr, resp)
        clients.append(client)
        lock.release()
        with waiting_condition:
            waiting_condition.notify()
        print(f'[+] User {client} connected to the server!')
        conn.send(f'[+] Successfully connected to the server!\n[+] Waiting for another user to connect...'.encode('utf-8'))
    except Exception as e:
        print(f'[!] Error: {e}')

def start_server():
    print(f'[+] Initializing server -> ({SERVER_HOST}, {SERVER_PORT})')
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection_handler_thread = threading.Thread(target=connection_handler)
    connection_handler_thread.daemon = True
    connection_handler_thread.start()
    try:
        server_socket.bind((SERVER_HOST, SERVER_PORT))
    except socket.error as msg:
        print(msg)
        sys.exit(-1)
    try:
        server_socket.listen()
        while True:
            conn, addr = server_socket.accept()
            print('[+] Connection with %s : %s ' %(addr[0], str(addr[1])))
            thread = threading.Thread(target=login_user, args=(conn, addr))
            thread.daemon = True
            thread.start()  
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
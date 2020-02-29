#!/usr/bin/env python3
import socket
import struct
import time
import threading
import traceback
import random

debug = 1

class PeerConnection:
    def __init__(self, peer_id, host, port, sock=None):
        self.debug = debug
        self.__peer_id = peer_id
        if sock:
            self.__sock = sock
        else:
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__sock.connect((host, int(port)))
        self.__cd = self.__sock.makefile('rw', None)

    def __debug(self, msg):
        if self.debug: print('\x1b[1;33;40m[DEBUG]\x1b[0m {msg}'.format(msg=msg))

    def __make_message(self, message_type, message_data):
        return struct.pack("4s4s{data_length}s".format(data_length=str(len(message_data))), message_type, message_data_length, message_data)

    def send_data(self, message_type, message_data):
        try:
            message = self.__make_message(message_type, message_data)
            self.__cd.write(message)
            self.__cd.flush()
        except:
            if self.debug:
                self.__debug(traceback.print_exc())
                return False
        return True

    def recv_data(self):
        try:
            message_type = self.__cd.read(4)
            if not message_type: return (None, None)

            message_data_length = int(struct.unpack("!L", self.__cd.read(4))[0])
            message_data = ""

            while len(message_data) != message_data_length:
                data = self.__cd.read(min(2048, message_data_length - len(message_data)))
                if not len(data):
                    break
                message_data += data

            if len(message_data) != message_data_length:
                return (None, None)
        except:
            if self.debug:
                self.__debug(traceback.print_exc())
        return (message_type, message_data)

    def close(self):
        self.__sock.close()
        self.__sock = None
        self.__cd = None

    def __str__(self):
        return str(self.__peer_id)

class PeerToPeer:
    def __init__(self, maxpeers=None, serverport=None, serverhost=None, id=None):
        self.debug = debug
        self.__shutdown = False
        if maxpeers: self.__maxpeers = int(maxpeers)
        else: self.__maxpeers = 2
        if serverport: self.__serverport = int(serverport)
        else: self.__serverport = random.randint(2500, 2510)
        if serverhost: self.__serverhost = str(serverhost)
        else: self.__init_server_host()
        if id: self.__id = str(id)
        else: self.__id = '{serverhost}:{serverport}'.format(serverhost=str(self.__serverhost), serverport=str(self.__serverport))
        self.peers = []

        self.__debug("Create node with id " + str(self.__id))

    def __debug(self, msg):
        if self.debug: print('\x1b[1;33;40m[DEBUG]\x1b[0m {msg}'.format(msg=msg))

    def __error(self, msg):
        print('\x1b[1;31;40m[ERROR]\x1b[0m {msg}'.format(msg=msg))

    def __success(self, msg):
        print('\x1b[1;32;40m[SUCCESS]\x1b[0m {msg}'.format(msg=msg))

    def __init_server_host(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('www.ya.ru', 80))
        self.__serverhost = s.getsockname()[0]
        s.close()

    def __handle_peer(self, client_socket):

        self.__debug("Current Thread: {thread} | Connected to {peer}".format(thread=str(threading.currentThread().getName()), peer=str(client_socket.getpeername())))

        host, port = client_socket.getpeername()
        peer_connection = PeerConnection(None, host, port, client_socket)

        try:
            message_type, message_data = peer_connection.recv_data()
            self.__success("type: {type} | data: {data}".format(type=str(message_type), data=str(message_data)))
        except:
            self.__error(traceback.print_exc())

    def add_peer(self, id, host, port):
        if peer_id not in seld.peers:
            self.peers[id] = (host, int(port))
            return True
        else:
            return False

    def __search_peers(self):
        delay = 0.5
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(0.5)
        while not self.__shutdown:
            for i in range(2500, 2510):
                try:
                    connection = s.connect(('', i))
                    self.__success("Find {i} port".format(i=str(i)))
                    connection.close()
                except:
                    pass

    def make_server_socket(self, serverport):
        backlog = 5
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', serverport))
        s.listen(backlog)
        return s

    def start(self):
        s = self.make_server_socket(self.__serverport)
        s.settimeout(2)
        self.__debug("Server start: id {id} ({host}:{port})".format(id=str(self.__id), host=self.__serverhost, port=str(self.__serverport)))

        search_peers_thread = threading.Thread(target=self.__search_peers)
        search_peers_thread.start()

        while not self.__shutdown:
            try:
                self.__debug("Listening for connections...")

                # s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # s1.connect(('', self.__serverport))

                client_socket, client_address = s.accept()
                client_socket.settimeout(None)
                t = threading.Thread(target=self.__handle_peer, args=[client_socket])
                t.start()
                t.join()
            except KeyboardInterrupt:
                self.__debug("Stop (Keyboard Interrupt)")
                self.__shutdown = True
                continue
            except socket.timeout:
                self.__debug("Socket timeout")
                continue
            except:
                print(traceback.print_exc())

        self.__debug("Exit from <start>")

    @staticmethod
    def test_socket_connection():
        def client():
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.connect(('localhost', 8080))
            s.send(b'(Client) test')
            data = s.recv(1024)
            s.close()
            print(data)

        def server():
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('', 8080))
            s.listen(1)
            conn, addr = s.accept()
            while 1:
                data = conn.recv(1024)
                print("(Server) " + str(data))
                if not data:
                    break
                conn.send(data.upper())
            conn.close()

        server = threading.Thread(target=server)
        server.start()
        time.sleep(1)
        client = threading.Thread(target=client)
        client.start()

host = input('host: ')
port = input('port: ')

peer = PeerToPeer(None, port, host, None)
peer.start()

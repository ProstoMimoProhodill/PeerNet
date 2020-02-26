#!/usr/bin/env python3
import socket
import struct
import time

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
        if maxpeers: self.__maxpeers = int(maxpeers)
        else: self.__maxpeers = 2
        if serverport: self.__serverport = int(serverport)
        else: self.__serverport = 8080
        if serverhost: self.__serverhost = str(serverhost)
        else: self.__init_server_host()
        if id: self.__id = str(id)
        else: self.__id = '{serverhost}:{serverport}'.format(serverhost=str(self.__serverhost), serverport=str(self.__serverport))

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
        host, port = client_socket.getpeername()
        peer_connection = PeerConnection(None, host, port, client_socket)

        try:
            message_type, message_data = peer_connection.recv_data()
        except:
            self.__error(traceback.print_exc())

    def make_server_socket(self, serverport):
        backlog = 5
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', serverport))
        s.listen(backlog)
        return s

    def start(self):
        s = self.make_server_socket(self.__serverport)
        s.settimeout(2)
        self.__debug("Server start: id {id} ({host}:{port})".format(id=str(self.__id), host=self.__serverhost, port=str(self.__serverport)))

        try:
            self.__debug("Listening for connections...")
            client_socket, client_address = s.accept()
            client_socket.settimeout(None)
            


net = PeerToPeer()
net.start()

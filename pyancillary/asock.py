import os
import socket
import selectors

# This is Awesome Socket, (Async Socket)

class ASock(object):
    def __init__(self, sock=None, stype=socket.AF_INET):
        if sock != None:
            self.sock = sock
        else:
            self.sock = socket.socket(stype, socket.SOCK_STREAM)
        self.buff = ""

    #TODO make this asycn
    def accept(self):
        return self.sock.accept()

    def close(self):
        return self.sock.close()
    
    # async connect
    #ex yield asock_instance.connect(host, port)
    def connect(self, host, port):
        self.sock.setblocking(0)
        self.sock.connect_ex((host, port))
        self.sock.setblocking(1)
        return ASIocConnect(self)

    def fileno(self):
        return self.sock.fileno()

    def bind_and_listen(self, host, port):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.sock.listen(10)

    def send(self, data):
        try:
            self.sock.send(data)
        except socket.error:
            return False
        return True

    # yeilds immediately when data is present in socket buffer
    def recv(self):
        if len(self.buff) > 0:
            r = self.buff
            self.buff = ""
            return r
        else:
            return ASIoc(self, "")

    # yields when pattern found in socket buffer
    def recv_p(self, pattern):
        indx = self.buff.find(pattern)
        if indx != -1:
            r = self.buff[:indx+len(pattern)]
            self.buff = self.buff[indx+len(pattern):]
            return r
        buff = self.buff
        self.buff = ""
        return ASIocPattern(self, buff, pattern)

    # yields when lenght is present in socket buffer
    def recv_l(self, length):
        if len(self.buff) >= length:
            r = self.buff[:length]
            self.buff = self.buff[length:]
            return r
        buff = self.buff
        self.buff = ""
        return ASIocLen(self, buff, length)


class ASIoc(object):
    def __init__(self, asock, buff):
        self.asock = asock
        self.buff = buff
        self.event = selectors.EVENT_READ

    def callback(self):
        try:
            rcv = self.asock.sock.recv(65536)
        except socket.error:
            rcv = ""
        return rcv

class ASIocLen(ASIoc):
    def __init__(self, asock, buff, length):
        super(ASIocLen, self).__init__(asock, buff)
        self.length = length

    def callback(self):
        try:
            rcv = self.asock.sock.recv(65536)
        except socket.error:
            rcv = ""
        if rcv == "":
            self.asock.buff = self.buff
            return ""
        self.buff += rcv
        if len(self.buff) >= self.length:
            r = self.buff[:self.length]
            self.asock.buff = self.buff[self.length:]
            return r

class ASIocPattern(ASIoc):
    def __init__(self, asock, buff, pattern):
        super(ASIocPattern, self).__init__(asock, buff)
        self.pattern = pattern

    def callback(self):
        try:
            rcv =  self.asock.sock.recv(65536)
        except socket.error:
            rcv = ""
        if rcv == "":
            self.asock.buff = self.buff
            return ""
        self.buff += rcv
        indx = self.buff.find(self.pattern)
        if indx != -1:
            r = self.buff[:indx+len(self.pattern)]
            self.asock.buff = self.buff[indx+len(self.pattern):]
            return r


class ASIocConnect(ASIoc):
    def __init__(self, asock):
        super(ASIocConnect, self).__init__(asock, "")
        self.event = selectors.EVENT_WRITE

    def callback(self):
        return True

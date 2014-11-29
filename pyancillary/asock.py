import ancil
import os
import socket

class ASIoc(object):
    def __init__(self, asock, buff):
        self.asock = asock
        self.buff = buff

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

class ASock(object):
    def __init__(self, sock=None, fd=None, stype=socket.AF_INET):
        if sock != None:
            self.sock = sock
        else:
            self.sock = socket.socket(stype, socket.SOCK_STREAM)
        self.buff = ""

    def accept(self):
        return self.sock.accept()

    def close(self):
        return self.sock.close()

    def connect(self):
        return self.sock.connect()

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

    def recv(self):
        if len(self.buff) > 0:
            r = self.buff
            self.buff = ""
            return r
        else:
            return ASIoc(self, "")

    def recv_p(self, pattern):
        indx = self.buff.find(pattern)
        if indx != -1:
            r = self.buff[:indx+len(pattern)]
            self.buff = self.buff[indx+len(pattern):]
            return r
        buff = self.buff
        self.buff = ""
        return ASIocPattern(self, buff, pattern)

    def recv_l(self, length):
        if len(self.buff) >= length:
            r = self.buff[:length]
            self.buff = self.buff[length:]
            return r
        buff = self.buff
        self.buff = ""
        return ASIocLen(self, buff, length)


class AncilSock(ASock):
    def __init__(self, fd, frm):
        self.fd = fd
        self.frm = frm
        self.sock = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
        self.buff = ""

    def close(self):
        #self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        os.close(self.fd)
        # close the socket on both ends
        #self.frm.send("%d " % fd)

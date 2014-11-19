import socket

# IOC stands for IO-Completion. this class plays
# a vital role in execution_stack, all execution stacks 
# starts with an instance of this object

class ASockIoc(object):
    
    # basic supported recv types, this is explaied further
    # in ASock, recv_p, recv and recv_l implementation
    _RCV_TYP_SIMPLE = 0
    _RCV_TYP_PATTERN = 1
    _RCV_TYP_LEN = 2
    _RCV_TYP_ACCEPT_CONN = 3

    def __init__(self, asock, rcv_typ, rcv_typ_data=None, _buff=""):
        self.sock = asock.sock        
        self.asock = asock
        self.buff = _buff
        if rcv_typ == self._RCV_TYP_SIMPLE:
            self.rcv_typ = self._RCV_TYP_SIMPLE
        elif rcv_typ == self._RCV_TYP_LEN:
            self.rcv_typ = self._RCV_TYP_LEN
            self.rcv_len = rcv_typ_data
        elif rcv_typ == self._RCV_TYP_PATTERN:
            self.rcv_typ == self._RCV_TYP_PATTERN
            self.patter = rcv_type_data
        elif rcv_typ == self._RCV_TYP_ACCEPT_CONN:
            self.rcv_typ = self._RCV_TYP_ACCEPT_CONN
        else:
            raise ValueError("unable to initialize ASockIoc with unknown rcv_typ")

    def Ioc_Callback(self):
        if self.rcv_typ == self._RCV_TYP_SIMPLE:
            return self.sock.recv(65535)
        elif self.rcv_typ == self._RCV_TYP_LEN:
            self.buff += self.sock.recv(65535)
            if len(self.buff) >= self.rcv_len:
                self.asock.buff = self.buff[self.rcv_len:]
                return self.buff[:self.rcv_len]
        elif self.rcv_typ == self._RCV_TYP_PATTERN:
            self.buff += self.sock.rcv(65535)
            indx = self.buff.find(self.pattern)
            if indx != -1:
                self.asock.buff = self.buff[indx:]
                return self.buff[:indx]
        elif self.rcv_typ == self._RCV_TYP_ACCEPT_CONN:
            conn, addr = self.sock.accept()
            return (ASock(fromIoc=conn), addr)
        else:
            raise ValueError("recv type is unknown in ASockIoc instance")

# Awesome socket. This package provides a async wrapper around the tranditional 
# unix  socket. The Best parts are
# => yield ASock_Instance.recv()        Asynchronus read data available < 65535 bytes.
# => yield ASock_Instance.recv_l(123)     Asynchronus read till 123 bytes are received.
# => yield ASock_Instance.recv_p("pattern")   Asynchronus read till pattern encounterd.
# enjoy
class ASock(object):
    def __init__(self, isUnix=False, fromIoc=None):
        self.buff = ""
        if fromIoc != None:
            self.sock = fromIoc
        elif isUnix:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def bind_and_listen(self, host, port):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.sock.listen(10)

    def connect(self, host, port):
        # TODO connect is still synchronus make this async
        return self.sock.connect((host, port))

    def fileno(self):
        return self.sock.fileno()

    def accept(self):
        return ASockIoc(self, ASockIoc._RCV_TYP_ACCEPT_CONN) 

    def close(self):
        return self.sock.close()

    def send(self, msg):
        self.sock.send(msg)

    def recv(self):
        return ASockIoc(self, ASockIoc._RCV_TYP_SIMPLE, _buff=self.buff) 

    def recv_p(self, p):
        return ASockIoc(self, ASockIoc._RCV_TYP_PATTERN, rcv_typ_data=p, _buff=self.buff)

    def recv_l(self, l):
        return ASockIoc(self, ASockIoc._RCV_TYP_LEN, rcv_typ_data=l, _buff=self.buff)


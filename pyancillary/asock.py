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

    def __init__(self, asock, rcv_typ_data=None, _buff=""):
        self.sock = asock.sock        
        self.asock = asock
        self.buff = _buff
        if rcv_typ_data == None:
            self.recv_type = _RCV_TYP_SIMPLE
        elif type(rcv_typ_data) is int:
            self.recv_type = _RCV_TYP_LEN
            self.recv_len = rcv_typ_data
        elif type(rcv_typ_data) is str:
            self.recv_type == _RCV_TYP_PATTERN
            self.patter = rcv_type_data 

    def Ioc_Callback(self, sock):
        assert sock == self.sock
        if self.recv_type == self._RCV_TYP_SIMPLE:
            return self.sock.recv(65535)
        elif self.recv_type == _RCV_TYP_LEN:
            self.buff += self.sock.recv(65535)
            if len(self.buff) >= self.recv_len:
                self.asock.buff = self.buff[self.recv_len:]
                return self.buff[:self.recv_len]
        elif self.recv_type == _RCV_TYP_PATTERN:
            self.buff += self.sock.recv(65535)
            indx = self.buff.find(self.pattern)
            if indx != -1:
                self.asock.buff = self.buff[indx:]
                return self.buff[:indx]
        else:
            raise ValueError("recv type is unknown in AsockIoc instance")

# Awesome socket. This package provides a async wrapper around the tranditional 
# unix  socket. The Best parts are
# => yield ASock_Instance.recv()        Asynchronus read data available < 65535 bytes.
# => yield ASock_Instance.recv_l(123)     Asynchronus read till 123 bytes are received.
# => yield ASock_Instance.recv_p("pattern")   Asynchronus read till pattern encounterd.
# enjoy
class ASock(object):
    
    def __init__(self, isUnix=False):
        self.buff = ""
        if isUnix:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def bind_and_listen(self, host, port):
        self.sock.bind((host, port))
        self.listen(10)

    def fileno(self):
        return self.sock.fileno()

    def accept(self):
        return self.sock.accept()

    def close(self):
        return self.sock.close()

    def send(self, msg):
        self.sock.send(msg)

    # ex: yield ASock_Instance.recv()
    # getts the maximum data from the socket buffer
    def recv(self):
        pass
    
    def recv_p(self, pattern):
        pass

    def recv_l(self, length):
        pass

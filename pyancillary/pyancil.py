from os import path
import socket
from cffi import FFI
ffi = FFI()

ffi.cdef("""
    int ancil_send_fd(int, int);
    int ancil_recv_fd(int, int *);
""")

complete_path = path.dirname(path.abspath(__file__))
lib = ffi.verify(""" #include "ancillary.h" """, 
        sources=[complete_path+"/fd_recv.c", complete_path+"/fd_send.c"],
        include_dirs=[complete_path])

def sendfd(sock, fd):
    return lib.ancil_send_fd(ffi.cast("int", sock.fileno()), ffi.cast("int", fd))


# return's the socket fd. In case of error, returns -1
def recvfd(sock):
    recv_fd = ffi.new("int *")
    recv_fd[0] = 0
    ret = lib.ancil_recv_fd(ffi.cast("int", sock.fileno()), recv_fd)
    if ret == 0:
        return int(recv_fd[0])
    else:
        return ret 

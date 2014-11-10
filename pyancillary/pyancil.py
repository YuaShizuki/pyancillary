from os import path
import socket
from cffi import FFI
ffi = FFI()

ffi.cdef("""
    int ancil_send_fd(int, int);
    int ancil_recv_fd(int, int *);
""")

lib = ffi.verify( """ #include "ancillary.h" """, 
                include_dirs=[path.dirname(path.abspath(__file__))],
                sources=["fd_recv.c", "fd_send.c"])

def sendfd(sock, fd):
    return lib.ancil_send_fd(ffi.cast("int", sock.fileno()), ffi.cast("int", fd))


# return's the socket fd. In case of error, returns -1
def recvfd(sock):
    recv_fd = cffi.new("int *")
    recv_fd[0] = 0
    ret = lib.ancil_recv_fd(ffi.cast("int", sock.fileno()), recv_fd)
    if ret == 0:
        return int(recv_fd)
    else:
        return ret 

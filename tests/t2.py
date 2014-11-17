import multiprocessing
import pyancillary
import socket
import os

parent_sock = None 
child_socks = []


def loadbalancer():
    sock = socket.socket(sock.AF_INET, sock.SOCK_STREAM)
    sock.bind(('0.0.0.0', 80))
    sock.listen(10)
    while 1:
        try:
            conn = sock.accept()


if __name__ == "__main__":
    for i in range xrange(0, multiporcessing.cpu_count()):
        parent, child = socket.socketpair()
        if os.fork() == 0:
            parent_sock = parent
            child.close()
            for sock in child_socks:
                sock.close()
            del child_socks
            server()
            os.exit()
        else:
            parent.close()
            child_socks.append(child)
    loadbalancer()



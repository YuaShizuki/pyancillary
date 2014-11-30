import ioloop
import asock
import socket
import multiprocessing
import os
import selectors

_connection_handler = None
_core_server_sock = None
_io_loop = None

def _process_accept_conn(notify):
    notify.recv(65536)
    conn, addr = _core_server_sock.accept()
    notify.send("0")
    aconn = asock.ASock(sock=conn)
    _io_loop.run_gen(_connection_handler, aconn, addr)

def process(notify, handler):
    global _connection_handler
    global _io_loop
    _connection_handler = handler
    _io_loop = ioloop.IoLoop()
    _io_loop.register_sock(notify, _process_accept_conn)
    _io_loop.run()


# handler is a genrator function, that would run concurently 
# handler has to be of type handler(conn, addr).
# conn is a new connection (ASock Instance) and addr is the address
# of the conenction
# remember load balancer launches multiple process's. All process's
# run the handler cuncurrently for every single connection accepted
def LoadBalancerLaunch(port, handler):
    global _core_server_sock
    _core_server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _core_server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    _core_server_sock.bind(('0.0.0.0', 80))
    _core_server_sock.listen(10)
    nodes = []
    for i in range(1, multiprocessing.cpu_count()):
        parent, node = socket.socketpair(socket.AF_UNIX)
        if os.fork() == 0:
            parent.close()
            process(node, handler)
            return
        node.close()
        nodes.append(parent)
    ioc = selectors.DefaultSelector()
    ioc.register(_core_server_sock, selectors.EVENT_READ, None)
    i = 0
    while True:
        evnts = ioc.select()
        for e in evnts:
            key, _ = e
            if key.fileobj != _core_server_sock:
                raise Exception("unknown registerd socket in selectors")
            nodes[i].send("0")
            nodes[i].recv(65536)
            if i >= (len(nodes)-1):
                i = 0
            else:
                i += 1

import ioloop
import asock
import ancil

class LoadBalancer(object):
    def __init__(self, nodes):
        self.ioloop = ioloop.IoLoop()
        self.sock = asock.ASock()
        self.indx = 0
        self.ioloop = ioloop.IoLoop()
        self.nodes = nodes
        #self.sock.bind_and_listen('0.0.0.0', 80)

    def handler(self, conn, addr):
        ancil.sendfd(self.nodes[self.indx], conn.fileno())
        if self.indx >= (len(self.nodes) - 1):
            self.indx = 0
        else:
            self.indx += 1
        conn.close()
        yield 0

    def close_time_wait_sock(self, sock):
        msg = sock.read(65535)
        all_fds = msg.strip().split(" ")
        for fd_s in all_fds:
            fd = int(fd_s)
            sock = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
            os.close(fd)

    def Run(self, port):
        #for node in self.nodes:
        #    self.ioloop.register_sock(node, close_time_wait_sock)
        self.ioloop.listen(port, self.handler)


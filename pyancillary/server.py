import load_balancer
import ioloop
import os
import socket
import multiprocessing 

def StartMultiProcessServer(port, handler):
    nodes = []
    for i in xrange(0, multiprocessing.cpu_count()):
        parent, node = socket.socketpair(socket.AF_UNIX)
        if os.fork() == 0:
            print "process(%d) ==> running" % os.getpid()
            ioloop.IoLoop().run_on_ancillary(node, handler)
            os.exit()
        nodes.append(parent)
    lb = load_balancer.LoadBalancer(nodes)
    lb.Run(port)

# simple hello world http server
import pyancillary.load_balancer as lb
import pyancillary.asock as asock
import os

def Handler(connection, address):
    request_header = yield connection.recv_p("\r\n\r\n")
    print "PID(%d) recived header =>\n%s\n" % (os.getpid(), request_header.strip())
    connection.send("HTTP/1.1 200 OK\r\n")
    connection.send("Content-Type: text/html; charset=UTF-8\r\n")
    connection.send("Connection: close")
    connection.send("Content-Length: 21\r\n\r\n")
    connection.send("<h1>hello_world</h1>\n")
    connection.close()

if __name__ == "__main__":
    lb.LoadBalancerLaunch(80, Handler)

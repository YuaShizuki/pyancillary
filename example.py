import pyancillary.load_balancer as lb
import pyancillary.asock as asock
import os


#this script acts as a proxy for pypy.org

def extract_content_length(header):
    keys = header.split("\r\n")
    for k in keys:
        if k.startswith("Content-Length:"):
            return int(k.split(": ")[1].strip())


def main(connection, address):
    get = asock.ASock()
    print "proxy recived connection on pid => %d" % os.getpid()
    yield get.connect("pypy.org", 80)
    get.send("GET / HTTP/1.1\r\nHost: pypy.org\r\n\r\n")
    header =  yield get.recv_p("\r\n\r\n")
    length = extract_content_length(header)
    content = yield get.recv_l(length)
    get.close()
    connection.send(header+content)
    connection.close()
    print "completed transaction on pid => %d" % os.getpid()


if __name__ == "__main__":
    lb.LoadBalancerLaunch(80, main)


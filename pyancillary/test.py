import httpp
import load_balancer
import os

def handler(conn, addr):
    print "recived connection on ==> %d" % os.getpid()
    while True:
        req = yield httpp.parse(conn)
        if req == None:
            conn.close()
            return
        html = "hello world"
        response = httpp.response(req['version'], html, httpp.keep_alive(req))
        conn.send(response)
        if not httpp.keep_alive(req):
            conn.close()
            return

def main(conn, addr):
    print "%d" % os.getpid()
    while True:
        request = yield httpp.parse(conn)
        if request == None:
            conn.close()
            return
        html = "hello world\n"
        header = "%s 200 OK\r\nContent-Type: text/html\r\nContent-Lenght: %d\r\n\r\n%s"
        response = header % (request['version'], len(html), html)
        conn.send(response)
        if not httpp.keep_alive(request):
            conn.close()
            return

if __name__ == "__main__":
    load_balancer.LoadBalancerLaunch(80, main)


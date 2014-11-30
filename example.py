import http
import load_balancer
import os

def main(conn, addr):
    print "%d" % os.getpid()
    while True:
        request = yield http.parse(conn)
        if request == None:
            conn.close()
            return
        html = "hello world\n"
        header = "%s 200 OK\r\nContent-Type: text/html\r\nContent-Lenght: %d\r\n\r\n%s"
        response = header % (request['version'], len(html), html)
        conn.send(response)
        if not http.keep_alive(request):
            conn.close()
            return

if __name__ == "__main__":
    load_balancer.LoadBalancerLaunch(80, main)


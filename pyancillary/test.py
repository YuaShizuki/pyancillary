import httpp
import server
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

if __name__ == "__main__":
    server.StartMultiProcessServer(80, handler)


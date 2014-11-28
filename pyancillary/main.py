import ioloop
import httpp

def tmp(conn, addr):
    while True:
        packet = yield conn.recv_p("\r\n\r\n")
        if packet == "":
            print "connection closed"
            conn.close()
            return
        print packet.strip().replace("\r\n", "|")
        msg = "<h1>hello world</h1>\n"
        header = "HTTP/1.1 200 OK\r\nContent-Length: %d\r\n\r\n" % len(msg)
        conn.send(header+msg)
    
def tmp2(conn, addr):
    while True:
        msg = yield conn.recv_p("__")
        if (msg == "") or (msg.strip() == "quit__"):
            print "___CLOSED____"
            conn.close()
            break
        print "%d => %s" % (addr[1], msg.strip()) 


def tmp3(conn, addr):
    while True:
        req = yield httpp.parse(conn)
        if req == None:
            conn.close()
            #print "connection forced closed"
            return
        html = ""
        for key in req:
            html += "<p>%s ==&gt %s</p>" % (key, req[key])
        response = httpp.response(req['version'], html, httpp.keep_alive(req))
        conn.send(response)
        if not httpp.keep_alive(req):
            #print "closing connection"
            conn.close()
            return

if __name__ == "__main__":
    ioloop.IoLoop().listen(80, tmp3)


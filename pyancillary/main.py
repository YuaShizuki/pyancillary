import ioloop

def main(conn, addr):
    print "connected =>"
    while True:
        packet = yield conn.recv_p("\r\n\r\n")
        if packet == "":
            conn.close()
            print "connection closed"
            break
        print packet.strip()
        msg = "<h1>hello world</h1>\n"
        header = "HTTP/1.1 200 OK\r\nConnection: close\r\nContent-Length: %d\r\n\r\n" % len(msg)
        conn.send(header+msg)
    

if __name__ == "__main__":
    ioloop.IoLoop().listen(80, main)


import pyancillary
import socket
import os

parent, child = socket.socketpair()

def child_process():
    child.close()
    loop = 0
    #data = parent.recv(1024)
    #print data.encode('hex')
    conn_fd = pyancillary.recvfd(parent)
    while conn_fd != -1:
        print "loop:%d" % loop
        try:
            conn = socket.fromfd(conn_fd, socket.AF_INET, socket.SOCK_STREAM, 0)
            msg = conn.recv(512)
            conn.send("hello world, with the help of pyancillary\n")
            # Its extremley important to close the socket by calling shutdown, close 
            # and finaly os.close on the final fd, since we recived a file discriptor. 
            # Not following these steps would lead to file discriptor leaks and sockets 
            # open in TIME_WAIT state.
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
            os.close(conn_fd)
        except:
            print "caught a error!"
        conn_fd = pyancillary.recvfd(parent)
        loop = loop + 1

def main_server():
    parent.close()
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.bind(('0.0.0.0', 80))
    serv.listen(5)
    print "(pid == %d) main server running on port 80 ..." % os.getpid()
    while 1:
        conn, addr = serv.accept()
        pyancillary.sendfd(child, conn.fileno())
        conn.close()

if __name__ == "__main__":
    if os.fork() == 0:
        child_process()
    else:
        main_server()

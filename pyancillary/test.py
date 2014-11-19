import asock
import core


def main():
    server = asock.ASock()
    server.bind_and_listen('0.0.0.0', 80)
    loop = 0
    while True:
        conn, _ = yield server.accept()
        loop += 1
        packet = yield conn.recv()
        print "%d" % loop
        conn.close()

if __name__ == "__main__":
    _ioc = core.Ioc(main())
    _ioc.Run()



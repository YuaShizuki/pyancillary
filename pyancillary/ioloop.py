import ancil
import asock
import socket
import types
import selectors

# Generator Container
class Slate(object):
    class Exhausted(object): 
        """return this in case of a exhausted generator"""
        def __init__(self, val):
            self.val = val

    class Halt(object):
        """return this to halt the genrator"""

    def __init__(self, gen=None, asioc=None):
       self.prev = None
       self.gen = gen
       self.gen_called = False
       self.asioc = asioc 

    def step(self, *args):
        if self.gen == None:
            raise ValueError("cant step forward on a non genrator slate")
        try:
            if not self.gen_called:
                self.gen_called = True
                r = self.gen.next()
            else: 
                r = self.gen.send(*args)
        except StopIteration:
            if len(args) > 0:
                return Slate.Exhausted(args[0])
            else:
                return Slate.Exhausted(None)
        if isinstance(r, types.GeneratorType):
            return Slate(gen=r)
        elif isinstance(r, asock.ASIoc):
            return Slate(asioc=r)
        else:
            return r

# Execution Stack
class ExStack(object):
    def __init__(self, selector):
        self.selector = selector

    def attachSocket(self, s, prev):
        assert s.asioc != None
        s.prev = prev
        self.selector.register(s.asioc.asock.sock, selectors.EVENT_READ, s)

    def follow(self, s, prev):
        s.prev = prev
        resp = None
        while not isinstance(resp, Slate.Exhausted):
            resp = s.step(resp)
            if isinstance(resp, Slate) and (resp.gen != None):
                resp = self.follow(resp, s)
                if isinstance(resp, Slate.Halt):
                    return resp
            elif isinstance(resp, Slate) and (resp.asioc != None):
                self.attachSocket(resp, s)
                return Slate.Halt()
        return resp.val

    def result(self, s, resp):
        while not isinstance(resp, Slate.Exhausted):
            resp = s.step(resp)
            if isinstance(resp, Slate) and (resp.gen != None):
                resp = self.follow(resp, s)
                if isinstance(resp, Slate.Halt):
                    return resp
            elif isinstance(resp, Slate) and (resp.asioc != None):
                self.attachSocket(resp, s)
                return Slate.Halt()
        if s.prev != None:
            self.result(s.prev, resp.val)

# IO Loop
class IoLoop(object):
    def __init__(self):
        self.selector = selectors.DefaultSelector()
        self.server_sock = None
        self.server_core_handler = None
        self.running_on_ancillary = False
        self.ex_stack = ExStack(self.selector)
    
    def run(self):
        while True:
            events = self.selector.select()
            for event in events:
                key, _  = event
                if key.fileobj == self.server_sock:
                    if self.running_on_ancillary:
                        fd = ancil.recvfd(self.server_sock)
                        conn = asock.AncilSock(fd, self.server_sock)
                        g = self.server_core_handler(conn, None)
                    else:
                        conn, addr = self.server_sock.accept()
                        g = self.server_core_handler(asock.ASock(sock=conn), addr)
                    s = Slate(gen=g)
                    self.ex_stack.follow(s, None)
                else:
                    if isinstance(key.data, Slate):
                        s = key.data
                        resp = s.asioc.callback()
                        if resp != None:
                            self.selector.unregister(key.fileobj)
                            self.ex_stack.result(s.prev, resp)
                    elif hasattr(key.data, "__call__"):
                        key.data(key.fileobj)
                    
    def listen(self, port, handler):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind(('0.0.0.0', port))
        self.server_sock.listen(10)
        self.server_core_handler = handler
        self.selector.register(self.server_sock, selectors.EVENT_READ, None)
        self.run()

    def run_on_ancillary(self, sock, handler):
        self.running_on_ancillary = True
        self.server_sock = sock
        self.server_core_handler = handler
        self.selector.register(self.server_sock, selectors.EVENT_READ, None)
        self.run()

    def register_sock(self, sock, handler):
        self.selector.register(sock, selectos.EVENT_READ, handler)

    def unregister_sock(self, sock):
        self.selector.unregister(sock)


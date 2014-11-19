import asock
import selectors
import types

class GenContainer():
    def __init__(self, _gen=None, _asock_ioc=None):
        if _gen == None and _asock_ioc == None:
            raise ValueError("no genrator or asock_ioc to wrap")
        self.gen = _gen
        self.asock_ioc = _asock_ioc
        self.frst_call = False
        self.nxt = None

class ExecutionStack():
    def __init__(self, ioc):
        self.ioc = ioc
        self.executing = []
        self.accepting_socks = []

    def notRegisterdAcceptingSock(self, gen):
        if gen.asock_ioc == None:
            return False
        if gen.asock_ioc.rcv_typ == asock.ASockIoc._RCV_TYP_ACCEPT_CONN: 
            if gen.asock_ioc.sock not in self.accepting_socks:
                return True
        return False

    def isReturnTypeForGen(self, r):
        if isinstance(r, types.GeneratorType):
            return False
        if isinstance(r, asock.ASockIoc):
            return False
        return True

    def wrap(self, gen):
        if isinstance(gen, types.GeneratorType):
            return GenContainer(_gen=gen)
        elif isinstance(gen, asock.ASockIoc):
            return GenContainer(_asock_ioc=gen)
        else:
            raise ValueError("recived return value to wrap")

    def attach(self, genrator, prev=None):
        if not isinstance(genrator, GenContainer):
            genrator_ = self.wrap(genrator)
        if genrator_.asock_ioc != None:
            genrator_.nxt = prev
            self.ioc.register(genrator_.asock_ioc.sock, selectors.EVENT_READ, genrator_)
            self.executing.append(genrator_)
        else:
            genrator_.nxt = prev
            r = genrator_.gen.next()
            if self.isReturnTypeForGen(r):
                raise ValueError("no need of a genrator that returns unblocking results")
            genrator_.frst_call = True
            self.attach(r, genrator_)
    
    def result(self, genrator, res):
        assert genrator.asock_ioc != None
        self.ioc.unregister(genrator.asock_ioc.sock)
        self.executing.remove(genrator)
        genrator_nxt = genrator.nxt
        while genrator_nxt != None:
            _r = genrator_nxt.gen.send(res)
            if isinstance(_r, types.GeneratorType):
                self.attach(_r, genrator_nxt)
                return
            elif isinstance(_r, asock.ASockIoc):
                node = self.wrap(_r)
                node.nxt = genrator_nxt
                self.executing.append(node)
                self.ioc.register(node.asock_ioc.sock, selectors.EVENT_READ, node)
                return
            res = _r
            genrator_nxt = genrator_nxt.nxt

    def recv(self, genrator):
        if (genrator not in self.executing) or (genrator.asock_ioc == None):
            raise ValueError("ASockIoc not registerd yet")
        _r = genrator.asock_ioc.Ioc_Callback()
        if _r != None:
            self.result(genrator, _r)

#IO-Completion Loop
class Ioc():
    def __init__(self, main):
        self.main = main
        self.ioc = selectors.DefaultSelector()
        self.ex_stack = ExecutionStack(self.ioc)
        self.running = False
    
    def Run(self):
        self.running = True
        self.ex_stack.attach(self.main, None)
        while self.running:
            evnts = self.ioc.select()
            for evnt in evnts:
                key, _ = evnt
                self.ex_stack.recv(key.data)


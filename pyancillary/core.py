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
    
    def install(self, gen, *args, *kwargs):
        gen, result = self.wrap(gen, args, kwargs)
        if gen == None:
            print result
            return None
        node = self.reap(gen)
        self.executing.append(node)
        return gen

    def reap(self, gen, result=None, _form_Ioc=False):
        if gen.asock_ioc != None:
            if _from_Ioc:
                result = gen.asock_ioc.Ioc_Callback()
                if result != None:
                    new_result = gen.nxt.send(result)
                    self.wrap(new_result, None, None)




    def wrap(self, gen, args, kwargs):
        if isinstance(gen, asock.ASockIoc):
            return (GenContainer(_asock_ioc=gen), None)
        result = gen(*args, **kwargs)
        if isinstance(result, types.GeneratorType):
            return (GenContainer(_gen=result), None)
        return (None, result)


#IO-Completion Loop
class Ioc():
    def __init__(self, main):
        self.main = main
        self.ioc = selectors.DefaultSelector()
        self.ex_stak = ExecutionStack(self.ioc)
        self.running = False
    
    def Run():
        self.running = True
        gen = self.ex_stack.install(main)
        if gen != None:
            self.ex_stack.reap(gen)
        while self.running:
            evnts = self.ioc.select()
            for evnt in events:
                key, _ = evnt
                self.ex_stack.reap(key.data, _from_Ioc=True)




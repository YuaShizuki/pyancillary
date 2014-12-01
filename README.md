pyancillary
===========
Pyancillary is async networking library for python, best performs on pypy.

why?
---
Pyancillary is multi process and concurrent. Unlike node cluster module that allows the operating system to do load balancing between process’s, Pyancillary equally distributes the load across all process’s evenly. This is vital since in a node cluster single process can accept a connection during high load when that connection could have been better served by another process which might have been dealing with 0 concurrent connections. Relying on the operating system for load balancing is inefficient when multiple cores are at your disposal

intalltion:
----------
```bash
$ git clone https://github.com/YuaShizuki/pyancillary.git
$ pypy setup.py
```
example:
-------
```python
# simple hello world http server
import pyancillary.load_balancer as lb
import pyancillary.asock as asock
import os

def Handler(connection, address):
    request_header = yield connection.recv_p("\r\n\r\n")
    print "PID(%d) recived header =>\n%s\n" % (os.getpid(), request_header.strip())
    connection.send("HTTP/1.1 200 OK\r\n")
    connection.send("Content-Type: text/html; charset=UTF-8\r\n")
    connection.send("Connection: close")
    connection.send("Content-Length: 21\r\n\r\n")
    connection.send("<h1>hello_world</h1>\n")
    connection.close()
                                    
if __name__ == "__main__":
    lb.LoadBalancerLaunch(80, Handler)
```
explanation:
------------
*   `def Handler(connection, address)` is the function called for every new connection
accepted on port 80 (http). 

*   `connection` is a asock (Awesome Socket) instance. Asock is detailed in asock.py

*   `yield connection.recv_p('\r\n\r\n')` yields when patter '\r\n\r\n' is recived in socket buffer. Hence in this case recives data till the end of http header is recived.

*   thats it folks enjoy, email me at yuashizuki@gmail.com

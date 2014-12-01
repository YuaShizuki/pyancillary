pyancillary
===========
Pyancillary is async networking library for python, best performs on pypy.

why?
---
Pyancillary is multi process and concurrent. Unlike node cluster module that allows the operating system to do load balancing between process’s, Pyancillary equally distributes the load across all process’s evenly. This is vital since in a node cluster single process can accept a connection during high load when that connection could have been better served by another process which might have been dealing with 0 concurrent connections. Relying on the operating system for load balancing is inefficient when multiple cores are at your disposal

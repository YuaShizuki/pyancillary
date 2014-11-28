def parse(conn):
    req = dict()
    packet = yield conn.recv_p("\r\n\r\n")
    if (packet == "") or (packet == None):
        yield None
    lines = packet.split("\r\n")
    
    if lines[0].startswith("GET"):
        req['method'] = "GET"
    elif lines[0].startwith("POST"):
        req['method'] = "POST"
    
    wrds = lines[0].split(" ")
    if len(wrds) != 3:
        yield None
    req['url'] = wrds[1]
    req['version'] = wrds[2].strip()

    for line in lines[1:-2]:
        wrds = line.split(":")
        if len(wrds) != 2:
            yield None
        req[wrds[0].strip()] = wrds[1].strip()
    yield req

def keep_alive(req):
    if req['version'] == "HTTP/1.0": 
        return False
    if ('Connection' in req) and (req['Connection'] == 'keep-alive'):
        return True
    return False

def response(version, content, connection=True):
    header = "%s 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length: %d\r\n"
    if not connection:
        header += "Connection: close"
    header += "\r\n\r\n"
    header = header % (version, len(content))
    return header+content



#!/usr/bin/env python

from __future__ import division, print_function

import os
import socket
import json
import sys
from syslog import *

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
sock.bind(('0.0.0.0', 20000))
sock.listen(2)

while True:
    conn, addr = sock.accept()
    try:
        data = conn.recv(4096)
        if data:
            json = json.loads(data)
            if json['command'] == 'shutdown':
                syslog(LOG_INFO, "SHUTDOWN")
                os.system("shutdown now -h");
    except:
        syslog(LOG_ERR, "Generic error")
        pass
    conn.close()
sock.close()
sys.exit(0)


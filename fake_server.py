#!/usr/bin/env python

import numpy
import socket
import sys
import os
import threading
import time
import zwoasi as asi
import json
from syslog import *
import argparse

# exit codes
EC_CAMERA_NOT_FOUND = 100
EC_GENERIC_ERROR = 110

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Fake ASI server')
    parser.add_argument('port_number', metavar='PORT', type=int, help='Server listening port')
    args = parser.parse_args()

    syslog(LOG_INFO, 'Start server')

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        sock.bind(('0.0.0.0', args.port_number))
        sock.listen(2)
        
        syslog(LOG_INFO, 'Waiting connections...')

        while True:
            conn, addr = sock.accept()

            try:
                data = conn.recv(4096)
                if data:
                    #print data
                    params = json.loads(data)
                    exp_time = params['exp_time']
                    gain = params['gain'] / 3
            except:
                pass

            try:
                image = numpy.array(numpy.random.random((960,1280))*gain,dtype=numpy.uint8)
                im_bytes = image.tobytes()

                chunk_size = 1024
                msg_len = len(im_bytes)

                for i in xrange((msg_len/chunk_size)+1):
                    start = i * chunk_size
                    end = start + chunk_size
                    if end > msg_len:
                        end = msg_len
                    conn.sendall(im_bytes[start:end])
            except Exception, e:
                pass

            conn.close()

    except Exception, e:
        print(e)
        sock.close()
        print('Generic error')
        syslog(LOG_ERR, 'Generic error')
        sys.exit(EC_GENERIC_ERROR)

    sock.close()


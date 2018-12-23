#!/usr/bin/env python

import numpy
import socket
import sys
import os
import threading
import time
import json
from syslog import *
import argparse
from PIL import Image

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Fake ASI server')
    parser.add_argument('port_number', metavar='PORT', type=int, help='Server listening port')
    args = parser.parse_args()

    syslog(LOG_INFO, 'Start server')

    # load image
    stars_img = Image.open('stars.png')
    im_arr = numpy.array(stars_img)

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        sock.bind(('0.0.0.0', args.port_number))
        sock.listen(2)
        
        syslog(LOG_INFO, 'Waiting connections...')
        print('Waiting....')

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

                im_rand = numpy.random.randint(low=0, high=15, size=1280*960, dtype=numpy.uint8).reshape(960, 1280)
                final = numpy.add(im_arr, im_rand)
                final[final > 255] = 255
                im_bytes = final.tobytes()
                chunk_size = 1024
                msg_len = len(im_bytes)

                for i in xrange((msg_len/chunk_size)+1):
                    start = i * chunk_size
                    end = start + chunk_size
                    if end > msg_len:
                        end = msg_len
                    conn.sendall(im_bytes[start:end])
            except Exception, e:
                print(e)
                pass

            conn.close()

    except Exception, e:
        sock.close()
        syslog(LOG_ERR, 'Generic error')
        sys.exit(1)

    sock.close()


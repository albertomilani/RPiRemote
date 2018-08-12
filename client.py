#!/usr/bin/env python

import socket
import sys
import threading
import time
import numpy as np
import json

HOST_ADDRESS = '192.168.10.44'
#HOST_ADDRESS = 'localhost'
HOST_PORT = 10000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)

def sendCaptureParams():
    print('Send params')
    params = {}
    params['exp_time'] = 1000
    params['gain'] = 150
    sock.sendall(json.dumps(params))

def receiveImage(connection):
    print('Receive image')
    arr = b''
    count = 0
    max_time = 5 # seconds
    time_start = time.time()

    while len(arr) < 1228800:
        now = time.time()
        if (now - time_start) > max_time:
            print('Timeout')
            break;
        data = connection.recv(2**16)
        if data:
            arr += data
    time_end = time.time()
    total_time = time_end - time_start
    print('Total time:', total_time)
    array = np.frombuffer(arr, dtype=np.dtype(np.uint8)).reshape((960,1280))
    print array

sock.connect((HOST_ADDRESS, HOST_PORT))

while True:
    th1 = threading.Thread( target=sendCaptureParams, args=() )
    th2 = threading.Thread( target=receiveImage, args=(sock,) )

    th1.start()
    th2.start()

    th1.join()
    th2.join()

sock.close()


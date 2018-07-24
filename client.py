#!/usr/bin/env python

import socket
import sys
import threading
import time
import numpy as np

HOST_ADDRESS = '192.168.10.44'
HOST_PORT = 10000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def sendCaptureParams():
    print('Send params')
    return
    while True:
        sock.sendall('cazzolo')
        time.sleep(0.02)

def receiveImage(connection):
    print('Receive image')
    arr = b''
    count = 0
    max_time = 5 # seconds
    time_start = time.time()
    #while len(arr) < 1228800:
    while len(arr) < 307200:
        if (time.time() - time_start) > max_time:
            print('Timeout')
            break;
        data = connection.recv(4096)
        if data:
            count = count + 1
            arr += data
    time_end = time.time()
    total_time = time_end - time_start
    print('Total time:', total_time)
    #array = np.frombuffer(arr, dtype=np.dtype(np.uint8)).reshape((960,1280))
    array = np.frombuffer(arr, dtype=np.dtype(np.uint8)).reshape((480,640))
    print array

sock.connect((HOST_ADDRESS, HOST_PORT))

th1 = threading.Thread( target=sendCaptureParams, args=() )
th2 = threading.Thread( target=receiveImage, args=(sock,) )

th1.start()
th2.start()

th1.join()
th2.join()

sock.close()

